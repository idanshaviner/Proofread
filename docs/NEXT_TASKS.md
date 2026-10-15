# Next engineering tasks

Use with `IMPLEMENTATION_STATUS.md`, `DECISIONS.md` and `OPEN_REQUIREMENTS.md`. Prioritize new owner instructions. Continue compatible offline work when external prerequisites are unavailable.

## Ready

1. **Expand held-out synthetic evaluation coverage.** Add invented multi-turn or adversarial-context scenarios for both generate and rewrite, with explicit intent/relevance review guidance. Preserve dataset versioning and regression evidence; no private data or authenticity-superiority claims.
2. **Review request-state regressions in the existing iOS harness.** Investigate editing/toggling inputs during an in-flight request and stale suggestion handling, using testable shared state where possible. Preserve the existing UX; native compilation/acceptance still requires Xcode.

## Blocked / prerequisites

- **Native app acceptance:** requires macOS/Xcode and signing access. Run an actual build and simulator generate/rewrite/copy checks; Foundation test success is not this acceptance gate.
- **Small live AI experiment:** requires secure key and current reviewed model/pricing/context/output-cap evidence, plus the intact one-time campaign ledger. Keep the mock default. Existing approval is one-time, not renewed by another task. No paid calls until every prerequisite is established.
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
