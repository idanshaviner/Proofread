"""Synthetic signed JWTs only: no Apple credentials, users, or live key fetches."""
import asyncio
import copy
import hashlib
import json
import time
import traceback

from cryptography.hazmat.primitives.asymmetric import rsa
import httpx
import jwt
import pytest

from app.apple_identity import AppleIdentityError, AppleIdentityVerifier


AUDIENCE = "com.example.proofread.synthetic"
NONCE = "synthetic-exact-nonce-claim"
ISSUER = "https://appleid.apple.com"
KEY_URL = "https://appleid.apple.com/auth/keys"


@pytest.fixture(scope="module")
def signing_keys():
    return [rsa.generate_private_key(public_exponent=65537, key_size=2048) for _ in range(3)]


def public_jwk(key, kid="synthetic-old"):
    result = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    result.update(kid=kid, use="sig", alg="RS256")
    return result


@pytest.fixture
def token(signing_keys):
    def make(*, updates=None, remove=(), key=None, kid="synthetic-old", algorithm="RS256", headers=None):
        now = int(time.time())
        claims = {"iss": ISSUER, "aud": AUDIENCE, "sub": "synthetic-subject",
                  "iat": now - 10, "exp": now + 300, "nonce": NONCE}
        claims.update(updates or {})
        for name in remove:
            claims.pop(name, None)
        return jwt.encode(claims, key or signing_keys[0], algorithm=algorithm,
                          headers={"kid": kid, **(headers or {})})
    return make


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def verifier_for(keys, *, clock=None, handler=None):
    calls = []

    def fetch(request):
        calls.append(request)
        assert request.method == "GET"
        assert str(request.url) == KEY_URL
        assert request.content == b""
        assert "authorization" not in request.headers
        assert "cookie" not in request.headers
        if handler:
            return handler(request)
        return httpx.Response(200, json={"keys": keys})

    return AppleIdentityVerifier(AUDIENCE, transport=httpx.MockTransport(fetch),
                                 monotonic_clock=clock or Clock()), calls


@pytest.mark.asyncio
async def test_valid_identity_returns_only_verified_subject(token, signing_keys):
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    identity = await verifier.verify(token(updates={"email": "invented@example.invalid",
                                                   "email_verified": False}), expected_nonce=NONCE)
    assert identity.subject == "synthetic-subject"
    assert vars(identity) == {"subject": "synthetic-subject"}
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("updates", [
    {"iss": "https://attacker.invalid"}, {"iss": "https://appleid.apple.com/"},
    {"iss": "appleid.apple.com"}, {"aud": "another-app"},
    {"aud": [AUDIENCE]}, {"aud": [AUDIENCE, "another-app"]},
    {"nonce": "wrong-nonce"}, {"nonce": ""}, {"nonce": None}, {"nonce": [NONCE]},
    {"sub": ""}, {"sub": "   "}, {"sub": 123}, {"sub": None},
    {"iat": int(time.time()) + 3600}, {"exp": int(time.time()) - 30},
    {"iat": 1, "exp": 1}, {"iat": True}, {"iat": "1"}, {"iat": 1.5},
    {"exp": str(int(time.time()) + 300)}, {"exp": float(int(time.time()) + 300)},
    {"exp": True}, {"iat": None}, {"exp": None},
    {"nbf": int(time.time()) + 3600}, {"nbf": True}, {"nbf": "1"},
    {"nonce": "\ud800"}, {"sub": "\ud800"},
])
async def test_invalid_claims_never_establish_identity(token, signing_keys, updates):
    verifier, _ = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError) as exc:
        await verifier.verify(token(updates=updates), expected_nonce=NONCE)
    assert exc.value.code == "invalid_token"


@pytest.mark.asyncio
@pytest.mark.parametrize("claim", ["iss", "aud", "exp", "iat", "sub", "nonce"])
async def test_required_claims(token, signing_keys, claim):
    verifier, _ = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError) as exc:
        await verifier.verify(token(remove=[claim]), expected_nonce=NONCE)
    assert exc.value.code == "invalid_token"


@pytest.mark.asyncio
async def test_nonce_is_exact_claim_without_implicit_hashing(token, signing_keys):
    verifier, _ = verifier_for([public_jwk(signing_keys[0])])
    digest = hashlib.sha256(NONCE.encode()).hexdigest()
    with pytest.raises(AppleIdentityError):
        await verifier.verify(token(updates={"nonce": digest}), expected_nonce=NONCE)
    assert (await verifier.verify(token(updates={"nonce": digest}), expected_nonce=digest)).subject
    unicode_nonce = "synthetic-🙂-nonce"
    assert (await verifier.verify(token(updates={"nonce": unicode_nonce}), expected_nonce=unicode_nonce)).subject


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_nonce", [None, "", " ", 1, "\ud800", "n" * 4097])
async def test_invalid_expected_nonce_rejected_without_network(token, signing_keys, bad_nonce):
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError):
        await verifier.verify(token(), expected_nonce=bad_nonce)
    assert calls == []


@pytest.mark.asyncio
async def test_forged_signature_rejected_without_refresh_storm(token, signing_keys):
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    forged = token(key=signing_keys[2])
    for _ in range(20):
        with pytest.raises(AppleIdentityError) as exc:
            await verifier.verify(forged, expected_nonce=NONCE)
        assert exc.value.code == "invalid_token"
    assert len(calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("algorithm", ["HS256", "none", "RS512"])
async def test_algorithm_allowlist_is_explicit_without_network(token, signing_keys, algorithm):
    now = int(time.time())
    claims = {"iss": ISSUER, "aud": AUDIENCE, "sub": "synthetic-subject",
              "iat": now - 10, "exp": now + 300, "nonce": NONCE}
    key = "synthetic-hmac-secret-long-enough-for-a-test" if algorithm == "HS256" else (
        None if algorithm == "none" else signing_keys[0])
    bad_token = jwt.encode(claims, key, algorithm=algorithm, headers={"kid": "synthetic-old"})
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError):
        await verifier.verify(bad_token, expected_nonce=NONCE)
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("header", [
    {"kid": ""}, {"kid": None}, {"kid": "x" * 129}, {"kid": "bad id"},
    {"jku": "https://attacker.invalid/keys"}, {"x5u": "https://attacker.invalid/cert"},
    {"jwk": {"kty": "oct", "k": "synthetic"}}, {"x5c": ["synthetic"]},
    {"crit": ["unknown"]}, {"crit": []}, {"b64": False},
])
async def test_untrusted_key_and_unsupported_headers_rejected_without_network(token, signing_keys, header):
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    segments = token().split(".")
    untrusted_header = jwt.get_unverified_header(".".join(segments))
    untrusted_header.update(header)
    segments[0] = jwt.utils.base64url_encode(json.dumps(untrusted_header).encode()).decode()
    with pytest.raises(AppleIdentityError):
        await verifier.verify(".".join(segments), expected_nonce=NONCE)
    assert calls == []


@pytest.mark.asyncio
@pytest.mark.parametrize("bad_token", [None, b"bytes", "", "not-a-token", "a.b.c", "x" * 16385])
async def test_malformed_token_input_has_safe_failure_without_network(signing_keys, bad_token):
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError) as exc:
        await verifier.verify(bad_token, expected_nonce=NONCE)
    assert exc.value.code == "invalid_token"
    assert calls == []


@pytest.mark.asyncio
async def test_deeply_nested_header_has_safe_failure_without_network(signing_keys):
    header = '{"alg":"RS256","kid":"synthetic-old","nested":' + '[' * 1200 + '0' + ']' * 1200 + '}'
    encoded = jwt.utils.base64url_encode(header.encode()).decode()
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError):
        await verifier.verify(encoded + ".e30.c2lnbmF0dXJl", expected_nonce=NONCE)
    assert calls == []


@pytest.mark.asyncio
async def test_unknown_kids_share_cooldown_and_new_key_rotates(token, signing_keys):
    clock = Clock()
    keys = [public_jwk(signing_keys[0])]
    verifier, calls = verifier_for(keys, clock=clock)
    for index in range(20):
        with pytest.raises(AppleIdentityError):
            await verifier.verify(token(kid=f"unknown-{index}"), expected_nonce=NONCE)
    assert len(calls) == 1
    clock.now += 60
    keys.append(public_jwk(signing_keys[1], kid="synthetic-new"))
    identity = await verifier.verify(token(key=signing_keys[1], kid="synthetic-new"), expected_nonce=NONCE)
    assert identity.subject == "synthetic-subject"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_same_kid_rotation_retries_signature_once_when_refresh_allowed(token, signing_keys):
    clock = Clock()
    keys = [public_jwk(signing_keys[0])]
    verifier, calls = verifier_for(keys, clock=clock)
    await verifier.verify(token(), expected_nonce=NONCE)
    keys[:] = [public_jwk(signing_keys[1])]
    clock.now += 60
    assert (await verifier.verify(token(key=signing_keys[1]), expected_nonce=NONCE)).subject
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_concurrent_valid_tokens_share_one_fetch(token, signing_keys):
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    identities = await asyncio.gather(*(verifier.verify(token(), expected_nonce=NONCE) for _ in range(20)))
    assert len(identities) == 20 and len(calls) == 1


@pytest.mark.asyncio
async def test_expired_cache_fails_closed_and_failed_refresh_is_throttled(token, signing_keys):
    clock = Clock()
    broken = False
    def handler(request):
        return httpx.Response(503, text="sensitive upstream failure") if broken else httpx.Response(
            200, json={"keys": [public_jwk(signing_keys[0])]})
    verifier, calls = verifier_for([], clock=clock, handler=handler)
    await verifier.verify(token(), expected_nonce=NONCE)
    broken = True
    clock.now += 901
    for _ in range(10):
        with pytest.raises(AppleIdentityError) as exc:
            await verifier.verify(token(), expected_nonce=NONCE)
        assert exc.value.code == "verification_unavailable"
    assert len(calls) == 2
    broken = False
    clock.now += 60
    assert (await verifier.verify(token(), expected_nonce=NONCE)).subject
    assert len(calls) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["status", "redirect", "invalid_json", "oversized", "too_many_keys",
                                 "duplicate_kid", "wrong_alg", "wrong_use", "wrong_kty", "bad_modulus",
                                 "private_material", "sign_operation", "no_keys", "bad_kid"])
async def test_invalid_jwks_is_safe_throttled_and_never_follows_token_urls(token, signing_keys, case):
    key = public_jwk(signing_keys[0])
    body = {"keys": [key]}
    if case == "too_many_keys":
        body = {"keys": [{**key, "kid": f"key-{index}"} for index in range(11)]}
    elif case == "duplicate_kid":
        body = {"keys": [key, copy.deepcopy(key)]}
    elif case == "wrong_alg": key["alg"] = "HS256"
    elif case == "wrong_use": key["use"] = "enc"
    elif case == "wrong_kty": key["kty"] = "oct"
    elif case == "bad_modulus": key["n"] = "!invalid!"
    elif case == "private_material": key["d"] = "synthetic-private-material"
    elif case == "sign_operation": key["key_ops"] = ["sign"]
    elif case == "bad_kid": key["kid"] = "bad kid"
    elif case == "no_keys": body = {"keys": []}
    def handler(request):
        if case == "status": return httpx.Response(503, text="sensitive-upstream-detail")
        if case == "redirect": return httpx.Response(302, headers={"location": "https://attacker.invalid/keys"})
        if case == "invalid_json": return httpx.Response(200, text="not JSON sensitive-upstream-detail")
        if case == "oversized": return httpx.Response(200, content=b"x" * 65537)
        return httpx.Response(200, json=body)
    verifier, calls = verifier_for([], handler=handler)
    for _ in range(2):
        with pytest.raises(AppleIdentityError) as exc:
            await verifier.verify(token(), expected_nonce=NONCE)
        assert exc.value.code == "verification_unavailable"
        rendered = "".join(traceback.format_exception(exc.value))
        assert "sensitive-upstream-detail" not in rendered
        assert NONCE not in rendered
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_small_rsa_public_key_is_rejected(token):
    weak = rsa.generate_private_key(public_exponent=65537, key_size=1024)
    verifier, _ = verifier_for([public_jwk(weak)])
    with pytest.raises(AppleIdentityError) as exc:
        await verifier.verify(token(), expected_nonce=NONCE)
    assert exc.value.code == "verification_unavailable"


@pytest.mark.asyncio
@pytest.mark.parametrize("error_type", [httpx.ReadTimeout, httpx.ConnectError])
async def test_transport_errors_do_not_leak_or_retry(token, signing_keys, error_type):
    def handler(request):
        raise error_type("sensitive transport detail", request=request)
    verifier, calls = verifier_for([], handler=handler)
    for _ in range(2):
        with pytest.raises(AppleIdentityError) as exc:
            await verifier.verify(token(), expected_nonce=NONCE)
        assert exc.value.code == "verification_unavailable"
        assert "sensitive transport detail" not in "".join(traceback.format_exception(exc.value))
    assert len(calls) == 1


@pytest.mark.parametrize("audience", [None, "", "   ", " spaced ", 123, "x" * 513])
def test_invalid_verifier_configuration_rejected(audience):
    with pytest.raises(ValueError):
        AppleIdentityVerifier(audience)


@pytest.mark.parametrize("options", [
    {"cache_ttl_seconds": 0}, {"cache_ttl_seconds": 3601}, {"cache_ttl_seconds": True},
    {"refresh_interval_seconds": 0}, {"refresh_interval_seconds": 301},
    {"cache_ttl_seconds": 60, "refresh_interval_seconds": 120},
])
def test_cache_configuration_stays_bounded(options):
    with pytest.raises(ValueError):
        AppleIdentityVerifier(AUDIENCE, **options)


@pytest.mark.asyncio
async def test_missing_key_id_rejected_without_network(token, signing_keys):
    segments = token().split(".")
    header = jwt.get_unverified_header(".".join(segments))
    del header["kid"]
    segments[0] = jwt.utils.base64url_encode(json.dumps(header).encode()).decode()
    verifier, calls = verifier_for([public_jwk(signing_keys[0])])
    with pytest.raises(AppleIdentityError):
        await verifier.verify(".".join(segments), expected_nonce=NONCE)
    assert calls == []


@pytest.mark.asyncio
async def test_total_fetch_timeout_cancels_slow_stream_and_throttles(token, monkeypatch):
    from app import apple_identity
    monkeypatch.setattr(apple_identity, "_FETCH_TIMEOUT_SECONDS", 0.01)
    cancelled = asyncio.Event()

    class SlowStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'{"keys": '
            try:
                await asyncio.sleep(10)
            finally:
                cancelled.set()
            yield b'[]}'

    verifier, calls = verifier_for([], handler=lambda _: httpx.Response(200, stream=SlowStream()))
    for _ in range(2):
        with pytest.raises(AppleIdentityError) as exc:
            await verifier.verify(token(), expected_nonce=NONCE)
        assert exc.value.code == "verification_unavailable"
    assert cancelled.is_set()
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_streamed_body_without_content_length_is_bounded(token):
    class OversizedStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b"x" * 32768
            yield b"x" * 32769

    verifier, calls = verifier_for([], handler=lambda _: httpx.Response(200, stream=OversizedStream()))
    with pytest.raises(AppleIdentityError) as exc:
        await verifier.verify(token(), expected_nonce=NONCE)
    assert exc.value.code == "verification_unavailable"
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_concurrent_unknown_kids_are_single_flight_while_fetch_is_pending(token, signing_keys):
    entered, release = asyncio.Event(), asyncio.Event()

    async def handler(request):
        entered.set()
        await release.wait()
        return httpx.Response(200, json={"keys": [public_jwk(signing_keys[0])]})

    verifier, calls = verifier_for([], handler=handler)
    tasks = [asyncio.create_task(verifier.verify(token(kid=f"unknown-{index}"), expected_nonce=NONCE))
             for index in range(20)]
    await asyncio.wait_for(entered.wait(), timeout=1)
    await asyncio.sleep(0)
    release.set()
    errors = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(error, AppleIdentityError) and error.code == "invalid_token" for error in errors)
    assert len(calls) == 1
