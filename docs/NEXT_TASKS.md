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

Keyboard direction: read owner source and `KEYBOARD_PROPOSAL.md`. The separate-keyboard synthetic feasibility spike is now approved; follow
`KEYBOARD_PROTOTYPE_TESTING.md` for actual Xcode/device acceptance. Await decisions
on draft-only API semantics, final UI and
shared session/data policy before implementation. Earlier indefinite keyboard
MVP deferral is superseded; current lack of extension/personalization remains real.
All host applications are untested and official Apple research is currently blocked.
Continue unrelated routine fixes while decisions/platform prerequisites are pending.

Approved keyboard spike source is implemented. Next platform gate: run the actual
Xcode build and synthetic cursor/selection/switching/permission/lifecycle checklist
in `KEYBOARD_PROTOTYPE_TESTING.md`. Latest shared suite 43/43 including local mock
HTTP integration; backend374/374. UIKit and all host apps remain unverified.
No additional implementation approval is needed to debug this approved spike, but
cloud networking, full typing UX, history/profile integration and release are not
included. Do not advance to daily private use on offline-model test evidence.

Native follow-up: owner's Xcode build now reaches source and exposed Observation
macro errors. The conditional declaration fix and a compiler regression check are
implemented; supply/apply the source patch and rerun actual Xcode validation.
Previous native status remains unverified until a successful Mac build, not merely
the passing Linux macro typecheck.

Device setup: confirm owner selected the installed extension via iOS globe rather
than launching only the containing app. Real device API use needs a reachable
trusted HTTPS backend and secure cost/auth prerequisites; localhost cannot reach
Mac from iPhone. New diagnostics make that failure actionable; no remote endpoint
was invented or deployed. Stream-backed fixture fix needs actual Mac rerun.

Research follow-up: read `CONTEXT_CAPTURE_RESEARCH.md` before claiming keyboard
context is categorically impossible or promising automatic screen access. Owner
reports iOS27.0.1; prioritize verified modern system capture APIs over deprecated
legacy ReplayKit and inspect actual Mac SDK headers. The owner has now approved
local-only synthetic capture/OCR testing and accepts possible Snap notifications.
Follow `LOCAL_CAPTURE_STUDY.md`; actual capture adapter/host behavior remains unverified.

Current capture blocker: get output from `ios/scripts/inspect-capture-sdk.sh` on
owner's Mac before writing the OS-specific capture adapter. Capture/OCR experiment
is approved; no repeat approval needed within its local-only synthetic limits.
Preparation self-test and 8 session-control tests are implemented, with54shared
passes/1optional skip. Do not describe this as implemented screen capture.
