# Internal Apple identity-token verifier foundation

The owner approved this backend-only foundation on October 15, 2026; see `AUTHENTICATION_PROPOSAL.md`. It is an internal library, not a login endpoint, middleware, session system or production authentication feature. Existing API routes remain unchanged. No private conversations or real user tokens are collected or stored.

## Use and trust boundary

```python
from app.apple_identity import AppleIdentityVerifier, AppleIdentityError

# Create once per configured audience/event loop and reuse across requests.
verifier = AppleIdentityVerifier(trusted_configured_audience)
identity = await verifier.verify(identity_token, expected_nonce=trusted_expected_nonce_claim)
# Only identity.subject is returned; do not use email as an account identifier.
```

The audience must come from trusted backend configuration, not the presented JWT or an arbitrary client field. The expected nonce must come from an independently established outstanding flow. It means the exact token claim: any platform-specific hashing belongs to the caller and is never guessed by the verifier. Successful verification alone does not consume a nonce, prevent token replay, create a session or authorize private-data access.

## Validated conservative contract

- Explicit RS256 allowlist and fixed Apple issuer; exact scalar audience; required signature, subject, nonce and integer expiry/issued-at claims. Future/expired/inconsistent times, malformed claims, forged tokens and unsupported JOSE key indirection fail closed.
- Fixed `https://appleid.apple.com/auth/keys` URL, TLS verification, no redirects or token-selected key URLs. The identity token/nonce is never sent to that public-key endpoint. Only public RSA signing keys with unique bounded IDs and 2048–8192-bit keys are accepted; private key fields and unsupported metadata are rejected.
- Five-second total fetch deadline in addition to HTTP phase timeouts; at most 64 KiB streamed JSON and ten keys. Default cache TTL is 900 seconds, refresh cooldown 60 seconds. Rotation and signature retries remain bounded; failed refreshes/unknown IDs share the cooldown. Expired keys are not used as a fallback.
- Per-instance async single-flight lock/cache only. Reuse the instance; creating one per request defeats the refresh bound. It is not a distributed rate limiter or a cross-worker cache.
- Frozen verified subject only; no email, raw JWT, nonce or upstream response returned. `AppleIdentityError.code` is `invalid_token` or `verification_unavailable`, with safe messages. Do not log the supplied token or dump decoded claims when handling errors. Normal task cancellation propagates.

## Evidence and limitations

103 synthetic signed-token tests and the full backend suite pass. Tests cover required/wrong claims, signature/algorithm attacks, nonce semantics, hostile headers/JWKS, key rotation, cooldown/concurrency, streamed size/total deadlines and error privacy. An independent code/security review and six additional malformed-key probes found no material blockers. There is no custom cryptography: PyJWT and cryptography perform JWT/RSA operations.

Maintained PyJWT documentation/source was verified through its official repository. Current Apple documentation and public JWKS requests returned HTTP proxy 403; this conservative contract has **not** been verified against live Apple identity tokens or the current vendor key set. Network-domain additions are saved in the environment draft, not assumed applied. Enable the required access, research the actual Apple contract, and validate compatibility before any real sign-in integration.

Dependency floors are the audited installed versions: `PyJWT[crypto]>=2.15.1,<3` and `cryptography>=50.0.2,<51`. Older PyJWT releases were excluded after PyPI advisory inspection. The installed 27-package environment had zero known pip-audit findings and zero skipped packages on October 15; this is a point-in-time advisory result, not a security guarantee.

Run from `backend`: `.venv/bin/python -m pytest -q tests/test_apple_identity.py`. All network traffic in tests is mocked. Live Apple sign-in, nonce issuance/consumption, replay protection, sessions/revocation, native UX, persistence, consent/deletion and tenant isolation remain separate reviewed milestones.
