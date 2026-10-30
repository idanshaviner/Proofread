# Next engineering tasks

Current checkpoint: October 30, 2026. Read `IMPLEMENTATION_STATUS.md` and
`REPOSITORY_ASSESSMENT.md`; earlier test counts in historical status entries are
not current acceptance results. Use synthetic data and mock inference by default.

## Continue independently

1. Review/publish the latest performance follow-through branch and its CI. No protected
   branch merge is authorized. Preserve the existing stacked feature history.
2. Bound the Swift client's response buffering before decoding; add oversized-body
   and cancellation regressions without changing the native workflow.
3. Design a small compatible review adapter for the two-case live report. Preserve
   failed/unrun cases and avoid expanding the approved call count. Current generic
   eight-case reports and live reports remain distinct; do not fabricate results.
4. Improve experimental manifests (exact prompt/config/code/model identity), then
   review the proposed synthetic personalization experiment with the owner.

## External acceptance gates

- **Live model validation:** secure key, refreshed same-day official evidence,
  availability preflight and intact campaign accounting are all required. The
  retained ledger reports zero reserved but belongs to another runtime, so it
  correctly blocks execution. Migration of that SAME campaign needs explicit
  review; never reset/recreate/rebind it or renew the $2 allowance implicitly.
- **Apple vendor acceptance:** after a meaningful environment access change, read
  current official contract and public keys. Do not retry unchanged blocked reads.
  Offline signature/key tests are not end-to-end Sign in with Apple acceptance.
- **Native iOS:** actual Mac/Xcode build plus simulator generate/rewrite/copy/error
  checks. Shared Swift Foundation tests do not compile SwiftUI on Linux. Signing
  is needed later for device/release, not initial unsigned simulator build.
- **Finalized documents:** owner exports go in `docs/source/`; current reconstructed
  PRD/SPEC/research/roadmap remain provisional. Do not repeatedly ask for exports.

## Decisions before major work

See assessment section H: minimal synthetic voice-conditioning experiment,
conversation-turn contract, sessions/privacy lifecycle, context-appropriate
candidate behavior, evaluation acceptance/budget and any paid native runner.
Current fixes do not authorize profile semantics, memory, storage, new recurring
costs, significant UX, production deployment or protected-branch merging.

Owner prerequisite instructions remain in `OWNER_SETUP.md`. The local preview is
mock-only; use its current README and updated bundle rather than older launchers.

Performance review follow-up: `PERFORMANCE_COST_REVIEW.md` records current evidence.
CI caching/stale cancellation and bounded oversized-input checks are implemented.
Prioritize HTTP client lifespan/pooling and measured admission/cost protection
before optimizing sub-millisecond offline reports; no paid benchmark is authorized
by the review. Trigger deduplication must preserve required checks and current
feature-branch coverage while PR API access is unavailable.


Latest follow-through: preview runtime/development dependencies are separated and
verified in a fresh runtime-only install. CI runs PRs/main pushes/manual dispatch,
so feature branches without a PR intentionally have no automatic push job. HTTP
connection lifetime tests and integrated results are in the current status entry.
Aggregate user quotas/concurrency policy, model/output tuning and private-response
caching remain decisions or experiments, not implied by connection-pool reuse.
