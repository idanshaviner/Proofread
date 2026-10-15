"""Internal, fail-closed Apple JWT verifier foundation; no sessions or persistence.

This conservative contract is approved for synthetic testing. Current Apple live
compatibility is unverified. Callers supply the expected *token nonce claim*,
including any platform-specific hashing themselves. Verification does not issue
nonces, consume them, prevent replay, or establish a production login session.
"""
import asyncio
from dataclasses import dataclass
import hmac
import json
import re
import time
from typing import Callable, Literal

from cryptography.hazmat.primitives.asymmetric import rsa
import httpx
import jwt


APPLE_ISSUER = "https://appleid.apple.com"
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
_FETCH_TIMEOUT_SECONDS = 5
_MAX_JWKS_BYTES = 65536
_MAX_KEYS = 10
_MAX_TOKEN_CHARS = 16384
_KID = re.compile(r"[A-Za-z0-9_-]{1,128}")
_TOKEN = re.compile(r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+")
_BASE64URL = re.compile(r"[A-Za-z0-9_-]+")
_UNSUPPORTED_HEADERS = {"crit", "b64", "jku", "jwk", "x5u", "x5c"}
_PRIVATE_JWK_FIELDS = {"d", "p", "q", "dp", "dq", "qi", "oth"}


class AppleIdentityError(Exception):
    """Safe failure category; contains no token, claims, URL or upstream body."""
    def __init__(self, code: Literal["invalid_token", "verification_unavailable"]):
        self.code = code
        super().__init__("Apple identity token is invalid" if code == "invalid_token"
                         else "Apple identity verification is unavailable")


@dataclass(frozen=True)
class AppleIdentity:
    subject: str


def _text(value, maximum):
    if not isinstance(value, str) or not 1 <= len(value) <= maximum or value.strip() != value:
        return False
    try:
        return bool(value.strip()) and all(character.isprintable() for character in value) and bool(value.encode("utf-8"))
    except UnicodeError:
        return False


class AppleIdentityVerifier:
    """Reuse one instance per configured audience, on one event loop.

    Cache, refresh cooldown and single-flight lock apply to this instance across
    all token key IDs, including failures. Creating an instance per request defeats
    that bound. This is not a distributed rate limiter. Expired keys are not used
    as a fallback when refresh is unavailable. TLS verification remains enabled.
    """
    def __init__(self, audience: str, *, transport: httpx.AsyncBaseTransport | None = None,
                 cache_ttl_seconds: int = 900, refresh_interval_seconds: int = 60,
                 monotonic_clock: Callable[[], float] = time.monotonic):
        if not _text(audience, 512):
            raise ValueError("A nonblank exact audience is required")
        if type(cache_ttl_seconds) is not int or not 60 <= cache_ttl_seconds <= 3600:
            raise ValueError("Cache TTL must be an integer between 60 and 3600 seconds")
        if (type(refresh_interval_seconds) is not int or not 30 <= refresh_interval_seconds <= 300
                or refresh_interval_seconds > cache_ttl_seconds):
            raise ValueError("Refresh interval must be between 30 and 300 seconds and at most the cache TTL")
        self.audience = audience
        self._transport = transport
        self._cache_ttl = cache_ttl_seconds
        self._refresh_interval = refresh_interval_seconds
        self._clock = monotonic_clock
        self._keys = {}
        self._expires_at = 0.0
        self._next_refresh_at = float("-inf")
        self._refresh_failed = False
        self._refresh_lock = asyncio.Lock()

    async def verify(self, identity_token: str, *, expected_nonce: str) -> AppleIdentity:
        """Verify signature and claims, comparing nonce exactly without hashing.

        The caller must obtain expected_nonce from a trusted outstanding flow,
        never from this unverified JWT. Only a verified subject is returned.
        """
        try:
            if (not isinstance(identity_token, str) or len(identity_token) > _MAX_TOKEN_CHARS
                    or not _TOKEN.fullmatch(identity_token) or not _text(expected_nonce, 4096)
                    or len(identity_token.split(".", 1)[0]) > 2048):
                raise AppleIdentityError("invalid_token")
            header = jwt.get_unverified_header(identity_token)
            kid = header.get("kid")
            if (header.get("alg") != "RS256" or not isinstance(kid, str)
                    or not _KID.fullmatch(kid) or _UNSUPPORTED_HEADERS.intersection(header)):
                raise AppleIdentityError("invalid_token")
            key = await self._key(kid)
            try:
                claims = self._decode(identity_token, key)
            except jwt.InvalidSignatureError:
                # Support rotation even when a publisher reuses a key ID. The
                # global per-instance cooldown also bounds forged-signature IO.
                key = await self._key(kid, force_refresh=True)
                claims = self._decode(identity_token, key)
            if (claims["iss"] != APPLE_ISSUER or claims["aud"] != self.audience
                    or type(claims["iat"]) is not int or type(claims["exp"]) is not int
                    or claims["exp"] <= claims["iat"]
                    or ("nbf" in claims and type(claims["nbf"]) is not int)
                    or not _text(claims["sub"], 512) or not _text(claims["nonce"], 4096)
                    or not hmac.compare_digest(claims["nonce"].encode("utf-8"), expected_nonce.encode("utf-8"))):
                raise AppleIdentityError("invalid_token")
            return AppleIdentity(subject=claims["sub"])
        except AppleIdentityError:
            raise
        except (jwt.PyJWTError, ValueError, TypeError, KeyError, RecursionError, OverflowError):
            raise AppleIdentityError("invalid_token") from None

    def _decode(self, token, key):
        return jwt.decode(token, key, algorithms=["RS256"], issuer=APPLE_ISSUER,
                          audience=self.audience, leeway=0,
                          options={"require": ["iss", "aud", "exp", "iat", "sub", "nonce"],
                                   "strict_aud": True})

    async def _key(self, kid, *, force_refresh=False):
        now = self._clock()
        if not force_refresh and now < self._expires_at and kid in self._keys:
            return self._keys[kid]
        async with self._refresh_lock:
            now = self._clock()
            if not force_refresh and now < self._expires_at and kid in self._keys:
                return self._keys[kid]
            if now < self._next_refresh_at:
                code = "verification_unavailable" if self._refresh_failed or now >= self._expires_at else "invalid_token"
                raise AppleIdentityError(code)
            self._next_refresh_at = now + self._refresh_interval
            self._refresh_failed = True
            keys = await self._fetch_keys()
            self._keys = keys
            self._expires_at = self._clock() + self._cache_ttl
            self._refresh_failed = False
            if kid not in keys:
                raise AppleIdentityError("invalid_token")
            return keys[kid]

    async def _fetch_keys(self):
        try:
            # HTTPX phase timeouts alone do not bound a slow stream's total time.
            async with asyncio.timeout(_FETCH_TIMEOUT_SECONDS):
                async with httpx.AsyncClient(timeout=_FETCH_TIMEOUT_SECONDS,
                                             transport=self._transport, follow_redirects=False) as client:
                    async with client.stream("GET", APPLE_JWKS_URL) as response:
                        response.raise_for_status()
                        content_length = response.headers.get("content-length")
                        if content_length is not None and int(content_length) > _MAX_JWKS_BYTES:
                            raise ValueError("Key response is too large")
                        content = bytearray()
                        async for chunk in response.aiter_bytes(chunk_size=4096):
                            content.extend(chunk)
                            if len(content) > _MAX_JWKS_BYTES:
                                raise ValueError("Key response is too large")
            return self._parse_keys(json.loads(content))
        except (httpx.HTTPError, TimeoutError, jwt.PyJWTError, ValueError, TypeError,
                KeyError, AttributeError, RecursionError, OverflowError):
            raise AppleIdentityError("verification_unavailable") from None

    @staticmethod
    def _parse_keys(document):
        raw_keys = document["keys"]
        if not isinstance(raw_keys, list) or not 1 <= len(raw_keys) <= _MAX_KEYS:
            raise ValueError("Invalid signing-key set")
        keys = {}
        for raw in raw_keys:
            kid = raw.get("kid")
            if (not isinstance(kid, str) or not _KID.fullmatch(kid) or kid in keys
                    or raw.get("kty") != "RSA" or raw.get("alg") != "RS256" or raw.get("use") != "sig"
                    or _PRIVATE_JWK_FIELDS.intersection(raw)
                    or ("key_ops" in raw and raw["key_ops"] != ["verify"])):
                raise ValueError("Invalid signing-key metadata")
            for name, maximum in (("n", 1400), ("e", 16)):
                value = raw.get(name)
                if not isinstance(value, str) or len(value) > maximum or not _BASE64URL.fullmatch(value):
                    raise ValueError("Invalid RSA key material")
            key = jwt.PyJWK.from_dict(raw, algorithm="RS256").key
            if not isinstance(key, rsa.RSAPublicKey) or not 2048 <= key.key_size <= 8192:
                raise ValueError("Unsupported RSA key size")
            keys[kid] = key
        return keys
