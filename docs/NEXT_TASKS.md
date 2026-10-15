# Next engineering tasks

Use with `IMPLEMENTATION_STATUS.md`, `DECISIONS.md` and `OPEN_REQUIREMENTS.md`. Prioritize new owner instructions. Continue compatible offline work when external prerequisites are unavailable.

## Ready

1. **Inspect current PR checks/review feedback and fix routine regressions.** Local integration is verified at 224 backend tests and 31 shared Swift tests; inspect checks for the latest pushed SHA rather than prior successful heads. Keep protected-branch merge gated on owner approval.

## Next selected milestone — decision pending

**Backend-only Apple token-verifier foundation:** see `AUTHENTICATION_PROPOSAL.md`. Owner was asked whether to approve this narrow milestone matching the provisional SPEC or defer identity code until finalized requirements. Do not infer approval. If approved, research Apple's current contract, implement synthetic signature/claim/key-rotation tests first, and keep sessions, UI, storage and production authentication explicitly deferred. Continue independently actionable fixes/reviews while awaiting the answer; do not repeatedly ask the same question.

## Blocked / prerequisites

- **Native app acceptance:** requires macOS/Xcode and signing access. Run an actual build and simulator generate/rewrite/copy checks; Foundation test success is not this acceptance gate.
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
