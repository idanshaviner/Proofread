# Approved authentication foundation — October 15, 2026

The owner explicitly approved the backend-only verifier foundation described here on October 15, 2026. Finalized identity/privacy requirements are not yet exported. Approval covers this small foundation, not production accounts, a new sign-in screen, sessions, persistent users or private-message storage.

## Proposed slice

Implement an internal Apple identity-token verifier with a maintained cryptographic JWT library rather than custom cryptography. Inputs are an identity token and the caller's expected audience and nonce. Verify Apple's issuer, explicit algorithm allowlist, signature against Apple's published keys, exact audience, expiry/issued-at constraints, subject and nonce. Support injectable key retrieval, bounded timeouts and safe failures. Never trust an unverified token's claims to authorize a user.

Acceptance: synthetic signed-token tests reject wrong issuer/audience/nonce, expired tokens, disallowed algorithms, missing claims and forged signatures; controlled key-rotation/unknown-key tests; no credentials, real user tokens, Apple sign-in flow or live inference required. Cache/key-fetch behavior must be bounded and must not leak tokens or arbitrary upstream errors. Research the current Apple contract from official documentation before implementation.

Execution checkpoint: current Apple research was attempted but blocked by proxy HTTP 403. The internal conservative JWT contract was implemented and tested against maintained PyJWT documentation/source and the explicit approved boundaries. 103 synthetic tests and independent security review passed. This does not satisfy the current-vendor/live compatibility gate; validate official Apple material when access is available before real sign-in integration. See `AUTHENTICATION.md`.

## Explicitly deferred

- No public authenticated route, production session or authentication-complete claim. Nonce issuance, replay protection, session lifecycle/revocation and device integration require the next reviewed slice.
- No storage, private history, consent/retention decisions, account linking or per-user data collection. Tenant isolation remains mandatory before those flows.
- No new paid identity provider, database, deployment, protected-branch merge, significant UX change or recurring expense.

## Recorded decision and tradeoff

**Approved:** implement the verifier foundation matching the existing proposed Apple direction. It advances offline-tested authentication without committing session/storage/UX policy; later finalized requirements could still require integration changes.

**Alternative:** defer authentication code until finalized identity requirements arrive, continuing existing offline/client work. This avoids even provisional identity integration but leaves the private-data roadmap blocked longer.

Neither option authorizes production authentication or private-data handling. Routine client validation, synthetic evaluation, code review and CI can continue independently while this decision is pending.
