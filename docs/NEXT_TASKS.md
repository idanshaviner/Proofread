# Next engineering tasks

Use with `IMPLEMENTATION_STATUS.md`, `DECISIONS.md` and `OPEN_REQUIREMENTS.md`. Prioritize new owner instructions. Continue compatible offline work when external prerequisites are unavailable.

## Ready

1. **Inspect current PR checks/review feedback and fix routine regressions.** Local integration is verified at 327 backend tests and 31 shared Swift tests; inspect each PR's latest pushed SHA. [PR #1](https://github.com/idanshaviner/Proofread/pull/1) has protocol/composer/evaluation work; [PR #2](https://github.com/idanshaviner/Proofread/pull/2) stacks the approved Apple foundation on it. After parent integration, adjust the child's base deliberately rather than rewriting shared history. Keep protected-branch merge gated on owner approval.

## Approved foundation — offline complete, vendor gate pending

**Backend-only Apple token-verifier foundation:** the owner approved this slice; do not ask again. Internal verification, 103 synthetic tests and independent security review are complete; see `AUTHENTICATION.md`. Current Apple docs/public keys returned proxy403, so live vendor compatibility is not accepted yet. After environment access changes, read official current contract/JWKS and validate the conservative assumptions without user tokens. Do not retry unchanged blocked requests. Sessions, replay prevention, UI, storage and production authentication remain outside this approval.

## Blocked / prerequisites

- **Native app acceptance:** requires macOS/Xcode and signing access. Run an actual build and simulator generate/rewrite/copy checks; Foundation test success is not this acceptance gate.
- **Apple compatibility:** apply the saved environment-domain additions for developer.apple.com/appleid.apple.com/pyjwt.readthedocs.io, then retry affected public reads. Secure Apple user credentials are not needed for these reads. If prerequisites remain unavailable, retain tested offline code without claiming sign-in integration.
- **Small live AI experiment:** requires secure key/account availability and the intact one-time campaign ledger. Official model/pricing/cap evidence was reviewed October 15 and retained outside Git; refresh on later dates. Conservative two-call reservation is $0.604608. Keep mock defaults and do not renew/reset the one-time allowance. No paid calls until every prerequisite is established.
- **Private history, personalization and retrieval:** reconcile approved identity/consent/deletion/isolation requirements before private data flows. Local synthetic research may proceed without collecting private conversations.
- **Consequential UX/product work:** finalized originals will arrive in `docs/source/`; ask only for decisions that materially block the selected implementation.
- **Remote review:** [draft PR #1](https://github.com/idanshaviner/Proofread/pull/1) contains the pushed feature branch and root operating instructions. Inspect its current checks and review before merge; default-branch tasks receive the new `AGENTS.md` after merge. No merge/release authorization is inferred.

## Completed foundation

- Provider validation, safe errors, mock edge cases and isolated offline tests.
- Shared Swift client, wire fixtures, real local Swift-to-FastAPI networking checks.
- Synthetic evaluation reports/blind-review templates and offline-tested one-time budget controls.
- Root engineering operating protocol with linked supporting procedures and durable task memory.
- Validated blinded-review summaries with optional verified-key unblinding; missing ratings and excluded cases remain distinct. Actual CLI smoke uses invented ratings only.
- Detached review/key objects and safe ordinary paired-write rollback, with meaningful failing tests captured before implementation. Crash-atomicity is not claimed.
- synthetic-v2: four original baseline cases preserved and four public, evaluation-only injection/contextual-intent stress cases added, with split/provenance/no-overlap checks. No AI quality evidence is implied.
- Composer stale request/copy/error cancellation and API-aligned Unicode input bounds; cancellation before generator execution prevents obsolete work. Shared state is tested; Apple UI adapter remains uncompiled.
- Backend/client whitespace distinctness parity, and official model/pricing/output-cap research without paid calls.
- Approved internal Apple verifier with 103 synthetic tests, independent security review and dependency audit. Vendor compatibility/replay/session/user-data gates remain explicit.

Follow-up checkpoint: both existing PRs had successful checks and no review comments
on inspection. Single-report artifact reliability is now covered alongside paired
writes (330 backend tests). Review the stacked follow-up PR before integration;
protected-branch merges remain gated. Continue with new review feedback or the
external acceptance prerequisites above when available.

Owner-input checkpoint: finalized exports, secure model key, macOS/Xcode runner,
and applied Apple-domain network access remain the external prerequisites. No new
routine-engineering clarification is required. Signing is needed for device/release
work, not the initial simulator build. Private-data policy/session design still
requires a concrete reviewed proposal before implementation. Latest local suite:
331 backend tests after safe offline CLI output-error handling.

Provider follow-up: total network deadline and streamed response-size protections
are implemented with 335 passing backend tests. During the already approved live
integration check, confirm the upstream honors identity content encoding; do not
claim vendor acceptance from offline tests. Review latest pushed CI and preserve
all existing paid-test, native-app and private-data gates.

Owner actions are consolidated in `OWNER_SETUP.md`; do not repeatedly request them.
After a reported settings change, recheck Apple reads/key presence before resuming
gated validation. Run `ios/scripts/validate-macos.sh` on an actual Mac and preserve
real build evidence; syntax/Linux checks alone are not native acceptance.
