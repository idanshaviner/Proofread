# Next engineering tasks

Use with `IMPLEMENTATION_STATUS.md`, `DECISIONS.md` and `OPEN_REQUIREMENTS.md`. Prioritize new owner instructions. Continue compatible offline work when external prerequisites are unavailable.

## Ready

1. **Validate and summarize completed blinded human reviews.** Extend the offline evaluation workflow to reject edited/mismatched review material, validate A/B/tie ratings and report per-dimension preference counts with missing ratings distinct. Test failures first, use invented data only, and make no statistical or personalization-superiority claim.
2. **Review evaluation artifact creation for partial writes.** Preserve existing outputs and make paired review/key failures explicit and recoverable; add a regression test before changing behavior. Keep the solution local and dependency-free.

## Blocked / prerequisites

- **Native app acceptance:** requires macOS/Xcode and signing access. Run an actual build and simulator generate/rewrite/copy checks; Foundation test success is not this acceptance gate.
- **Small live AI experiment:** requires secure key and current reviewed model/pricing/context/output-cap evidence, plus the intact one-time campaign ledger. Keep the mock default. Existing approval is one-time, not renewed by another task. No paid calls until every prerequisite is established.
- **Private history, personalization and retrieval:** reconcile approved identity/consent/deletion/isolation requirements before private data flows. Local synthetic research may proceed without collecting private conversations.
- **Consequential UX/product work:** finalized originals will arrive in `docs/source/`; ask only for decisions that materially block the selected implementation.
- **Remote PR workflow:** last GitHub Actions API read returned HTTP 403. Recheck only when needed or after a meaningful access change; retain validated local commits and PR details if remote operations remain unavailable.

## Completed foundation

- Provider validation, safe errors, mock edge cases and isolated offline tests.
- Shared Swift client, wire fixtures, real local Swift-to-FastAPI networking checks.
- Synthetic evaluation reports/blind-review templates and offline-tested one-time budget controls.
- Root engineering operating protocol with linked supporting procedures and durable task memory.
