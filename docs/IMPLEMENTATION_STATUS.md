# Implementation status — October 15, 2026

## Recovered project and scope

- Read all existing repository documentation and application/test sources. PRD, SPEC, AI architecture and roadmap remain provisional reconstructions; finalized originals and approved UI designs were not recovered from this checkout.
- `AGENTS.md` referenced a missing `DECISIONS.md`; a new engineering decision record captures actual implementation boundaries without claiming product approval.
- Preserve the current native SwiftUI developer harness and provisional FastAPI service. The product is not production ready.

## Implemented

- FastAPI health and generate/rewrite endpoints, with deterministic, explicitly nonpersonalized mock responses by default.
- Opt-in OpenAI structured-output adapter; now validates complete output, three distinct nonblank bounded candidates and nested response shape. Invalid/incomplete output, refusals, HTTP failures and transport errors fail safely with HTTP 502. Missing/unknown provider configuration returns HTTP 503.
- Provider requests have a 25-second client timeout, 2048 completion-token cap and no automatic retries. These are engineering bounds, not a production budget, rate limiter or quality guarantee.
- Fixed mock rewrite crashes for punctuation-only and maximum-length drafts. Long mock drafts are truncated to fit candidate limits; mock output cannot establish intent fidelity.
- SwiftUI harness retains generate/rewrite/copy flows. Shared Foundation networking supports injected ephemeral URLSession, configurable endpoint, safe errors, timeout/cancellation and response validation. A shared composer model invalidates/cancels on input/mode changes, rejects stale responses/errors, preserves newer loading, resolves copy text from current state and suppresses unsafe unknown errors. Client length checks use Unicode scalars to match existing API bounds. Native observation/view wiring is implemented but not Xcode-compiled; no significant UI redesign.
- Dependency-free Swift Package compiles the same models/client/configuration as the iOS app, with Python-verified synthetic wire fixtures and an opt-in real URLSession integration check against the mock backend.
- Signed official Swift 6.1.3 toolchain installed for Linux shared-source validation, with repeatable signature-verifying installation and writable-cache test scripts.
- Deterministic aggregate style extraction exists with synthetic tests. It remains disconnected from generation and persistence.
- Offline evaluation CLI runs eight invented generate/rewrite cases in `synthetic-v2`: four preserved baseline cases and four public untuned injection/contextual-intent stress cases. Split, provenance and example-overlap invariants are tested. Reports record contracts/provenance/latency and support blinded review; current dataset hashes intentionally reject old v1 reports. Quality remains unmeasured; no superiority claim.
- Separate live-integration runner supports the owner's one-time $2 `gpt-5.4-mini` authorization, up to two unchanged synthetic baseline requests, evidence/key/availability prerequisites, durable reservations before inference, usage accounting and explicit unrun cases. It stops on unknown outcomes and never refunds or retries. Same-day official evidence is now reviewed; credentials/account availability still block paid execution.
- Backend tests isolate provider environment variables and block live HTTP transports. Existing GitHub workflow explicitly selects mock mode.
- Root `AGENTS.md` now contains the owner's permanent Autonomous Engineering Operating Protocol, linked to `ENGINEERING_PROTOCOL.md` and durable `NEXT_TASKS.md`. Work proceeds on feature branches with validated commits and PR review; consequential uncertainty prompts questions throughout development.
- Resumed offline implementation: completed review validation and preference summaries with blinded or validated-key unblinded counts, missing/unrated/excluded outcomes distinct, and no quality claims. Fixed shared review/source references and ordinary paired-artifact write failures, with regression coverage written before fixes.
- Owner-approved internal Apple identity verifier now validates synthetic RS256 signatures, exact issuer/audience/nonce, strict required claims and subject-only results. Fixed-URL JWKS retrieval has total deadlines, size/key bounds, rotation, single-flight caching/cooldown and safe failures. It is not connected to API routes, sessions, user storage or native sign-in; current Apple vendor compatibility remains unverified.

## Verification in this cloud instance

- Baseline: 14 backend tests passed on Python 3.12.14 when run from `backend`, as required by `AGENTS.md`. An initial invocation from the repository root failed imports; this was a working-directory error, not a product defect.
- Latest backend: **327 passed**, no failures or skips, on Python 3.12.14, including 103 synthetic Apple verifier tests, 27 live-runner controls, 13 dataset invariant tests and five cross-language distinctness tests. One nonfatal Starlette TestClient/httpx deprecation warning. This run inherited `PROOFREAD_PROVIDER=openai`, proving test isolation still forces offline mocks. PyJWT/cryptography dependency additions pass `pip check`.
- Shared Swift networking/composer: **31 passed, no skips or failures**, including actual local URLSession generate/rewrite/HTTP 422. Behavioral tests failed before fixes for stale output/loading/copy, unknown-error privacy, Unicode input bounds, and cancellation/model release before task execution. Swift 6.1.3 on Linux compiles shared state transitions without the Apple Observation adapter. The package's Apple minimum is macOS 14; app minimum remains iOS 17. SwiftUI/Observation wiring, Xcode and simulator validation remain unrun.
- Swift installer signature/fingerprint verification and repeat execution succeeded without a second download. Both helper scripts passed shell syntax checks.
- Fresh FastAPI HTTP checks passed for health, generate, rewrite, punctuation-only rewrite, 10,000-character rewrite and missing-draft HTTP 422.
- Evaluation CLI run/compare commands executed with synthetic data: four contract passes and four blind-review cases. Reports and case counts were checked. These commands do not run live inference or establish quality.
- Actual offline CLI run → compare → invented ratings → summarize passed for four cases with validated unblinding. Ratings in this smoke test are fabricated acceptance-test data, not human quality evidence. Existing output preservation, changed material rejection and paired-write rollback have targeted tests.
- Updated synthetic-v2 CLI smoke passed with eight mock contract outcomes and partial invented ratings: four baseline votes/four missing stress ratings per dimension. Both live-test input requests are pinned unchanged. Backend distinctness now collapses internal whitespace before casefolding, matching Swift; spaces/tab/newline/NBSP variants failed four regressions before the fix.
- Canonical one-time approval ledger initialized once at `/workspace/.proofread/live-budget.json`, outside Git: available, zero calls reserved, **$0 paid expenditure**. Actual default live CLI invocation was blocked without changing that ledger. Both credential variable names remain unset. The ledger is bound to this runtime and cannot authorize a copied/rebooted campaign; cross-instance spending requires stronger coordination, not reinitialization.
- GitHub API access recovered after earlier HTTP 403 responses: original `main` CI is verified successful, as are prior PR-head checks at `ca0e2c1`. New branch commits require their own checks. Official OpenAI model/pricing/reference documentation also recovered: structured output/default-tier support and billing bounds were reviewed October 15. The approved global/default-tier two-call reservation is $0.604608; see `AI_EVALUATION.md`. No authenticated availability or live inference is implied.
- Feature branch `codex/autonomous-engineering-protocol` is pushed and [draft PR #1](https://github.com/idanshaviner/Proofread/pull/1) is open. Initial branch-push backend CI at `1c760ee` passed; consult the PR for checks on subsequent documentation commits. No merge or release occurred. Root instructions are automatically discoverable on this branch; default-branch tasks receive them after merge.
- PR #1 backend checks at the completed composer/evaluation head `5d5bacc` passed. The approved internal verifier is pushed on stacked branch `codex/apple-verifier-foundation` in [draft PR #2](https://github.com/idanshaviner/Proofread/pull/2), based on PR #1. Its current checks/review are separate; neither branch has been merged or released.
- Independent verifier review reran all 103 targeted tests and six additional hostile-key probes without finding material blockers. Installed dependency audit: 27 packages, zero known findings, zero skipped. Audited PyJWT 2.15.1/cryptography 50.0.2 are the declared minimums; vulnerable older PyJWT ranges were excluded based on PyPI advisory evidence. This is not a security guarantee.
- Official PyJWT documentation/source was read from its maintained repository. Apple developer documentation and public JWKS requests returned proxy HTTP 403. Additive access requirements are saved for `developer.apple.com`, `appleid.apple.com` and `pyjwt.readthedocs.io`; draft saving does not establish current reachability. No real identity tokens or live Apple verification ran.

## Outstanding gates

- **Live model behavior:** the owner approved `gpt-5.4-mini` with a one-time $2 maximum. Secure credentials and authenticated account availability remain unavailable; official evidence was reviewed October 15 and must be refreshed on later dates. The bounded runner has offline control tests; no paid calls ran and the original ledger remains unused.
- **Native app:** no Xcode, simulator, device, signing or SwiftUI compilation ran here. Run XcodeGen and actual Xcode build/acceptance on macOS. Linux Foundation tests cannot satisfy this gate.
- **Privacy and identity:** an internal verifier exists, but end-to-end authentication, challenge/nonce consumption, replay protection, sessions, consent/deletion, persistence and tenant isolation remain unimplemented. Do not store or import private conversations. Database/session/privacy choices remain undecided.
- **Approved identity foundation:** the owner explicitly approved `AUTHENTICATION_PROPOSAL.md`. Offline implementation/tests/security review are complete; current Apple contract/JWKS validation remains blocked by network access. Sessions, native UI and private data remain outside that approval. See `AUTHENTICATION.md`.
- **Personalization:** no public personalized-generation API, contextual retrieval, feedback learning or measured authenticity improvement. Local aggregate extraction and evaluation infrastructure are foundations only.
- **Product direction:** finalized exports will arrive in `docs/source/` from the owner's ChatGPT Project. Continue compatible offline work while awaiting them; reconcile approved workflows before consequential UX, scope, architecture, privacy or release changes. See `OPEN_REQUIREMENTS.md` for the concise material requirements list.

## Next bounded milestones

1. Execute Xcode app build and simulator generate/rewrite acceptance on macOS using the tested shared client.
2. Run a bounded, explicitly authorized synthetic live-model experiment and record actual model/configuration, cost and failures.
3. Reconcile finalized product sources, then implement approved authentication/consent/deletion and isolation before adding private data flows.
4. Add authorized personalization and contextual retrieval incrementally, using blinded evaluation against generic AI before claiming a quality gain.

## Reusable environment configuration

Saved the tested Python/Swift installation script and startup instructions, mock-provider/model suggestions, a secure `PROOFREAD_OPENAI_API_KEY` requirement scoped to `api.openai.com`, and network additions for that API, official OpenAI documentation/pricing and GitHub Actions status reads. The platform reserves `OPENAI_` variable names, so the backend supports the `PROOFREAD_` alias while preserving legacy local configuration.

Draft persistence is confirmed. These changes have not been published or validated in a new task. Enter the key securely and review/save/publish through environment settings when appropriate; this never authorizes automatic paid calls or ledger reset. Startup and installation remain offline with respect to inference.

### Evaluation output follow-up

Single offline reports and review summaries now share the paired artifact writer's
UTF-8, exclusive 0600 creation, pre-serialization, flush/fsync and identity-checked
rollback safeguards. Existing outputs are preserved. Serialization and durability
failures were reproduced before the fix; the full backend suite passes 330 tests
(one existing Starlette deprecation warning). This is ordinary-failure protection,
not crash-atomic publication or protection against adversarial directory mutation.
No AI calls, authentication scope changes or native iOS checks were involved.

The follow-up also normalizes offline `run` output failures to an actionable CLI
usage error (exit 2), without leaking underlying storage diagnostics. Regression
reproduced first; full backend suite: 331 passed, one existing warning. PR #3's
preceding commit passed remote CI; this subsequent commit requires its own CI run.

### Provider response resource bounds

OpenAI response fetching now has a 25-second total network deadline, a 256 KiB
streamed body limit and identity-only content encoding (requested and checked
before body decoding). Oversized replies stop early and close the response.
Timeouts remain safe provider failures; there are no retries. Existing schema and
accounting validation still run after fetching. Two defects were reproduced before
implementation; boundary and compression regressions were added. Full backend:
335 passed, one existing deprecation warning. All requests used offline transports;
real provider compatibility remains gated on credentials and the controlled test.

### Owner prerequisite handoff

PR #3's provider-limits commit passed remote backend CI. Existing cloud draft
inspection confirms Apple domains are listed and the model secret has no saved
binding; saving is not runtime application/publication. `OWNER_SETUP.md` provides
secure configuration, finalized-export and local Mac instructions. The new Mac
validation script has passed Bash syntax and Linux refusal checks; its unsigned
Xcode build path remains unexecuted. No hosted macOS cost or paid inference was
introduced. Routine engineering remains independent of these external actions.

### Local browser preview

`tools/preview/start.command` starts a loopback-only developer harness backed by
existing API routes and forced mock mode. This is an explicitly requested testing
artifact, not a new native design. HTTP smoke verified HTML/no-store, generate,
rewrite and invalid-input responses. Browser rendering/clipboard and Mac launcher
execution remain unverified. No AI or private storage is enabled.

### October 30 professional assessment (read-only application audit)

See `REPOSITORY_ASSESSMENT.md` for A–I product/architecture/AI/code assessment and
approval proposals. Current backend: 335 passed; pip check clean. Shared Swift:
30 passed, 1 optional local API test skipped, no native Xcode execution. Confirmed
launcher recovery, Unicode contract and privacy/resource findings are documented;
application code is unchanged during this assessment. Read-only live-ledger review
found zero reserved but a different runtime fingerprint: paid execution remains
blocked, and the ledger was not reset/rebound. Previous model evidence is stale.

### October 30 audit fixes — integrated verification

Fixed launcher interpreter preflight/recovery without deleting existing environments;
422 input/context echo; formatted provider diagnostic privacy; NFC reply uniqueness;
compressed Apple-key response handling; and unbounded live-model preflight. Each
behavior change has a regression captured failing before implementation. Updated
shared error and Unicode fixtures preserve Python/Swift contract checks.

Integrated backend: **364 passed**, one existing Starlette/httpx warning. Shared
Swift against a real local mock FastAPI server: **32 passed**, no skips/failures.
The actual updated launcher reused a healthy environment and preview HTTP generate,
rewrite and redacted invalid-input smoke passed on Linux. Launcher selection and
failed-install recovery tests use disposable fake interpreters without network.
Mac/Xcode/browser clipboard and Python 3.15 compatibility remain unverified; the
launcher accepts 3.11–3.13, with cloud execution verified on 3.12. No paid inference,
canonical campaign-ledger changes, private storage or personalization change.

Remaining audit work: Swift bounded response receiving, live-report review adapter
and richer experiment manifests. Those are not claimed complete by this batch.

### October 30 performance/cost review

Reviewed backend/AI, evaluation/ledger, native/preview, setup and CI paths; see
`PERFORMANCE_COST_REVIEW.md` for ranked opportunities and trade-offs. Implemented
pip caching and same-event/ref stale-run cancellation in mock-only backend CI;
workflow YAML parsed and fields checked locally, remote savings unmeasured.
Bounded Swift input-length checking now precedes trimming for enormous invalid
pastes, preserving codepoint and nonblank rules. Added large-paste/Unicode boundary
coverage. Backend: 364 passed (one existing warning). Shared Swift: 32 passed,
1 optional local-API skip, 0 failures; no Xcode execution. Paid-call counts and
ledger state were not changed. No model/provider, privacy or product changes.

Eight-case blind-review preparation benchmark: 100 runs, median 0.475 ms,
max 0.770 ms locally. Additional HTTP client construction, forwarded unused draft,
style-memory and unbounded concurrency probes identify potential work but do not
measure live latency/cost. Preserve integrity and budget durability rather than
micro-optimizing their checks. Reuse outbound HTTP connections, bounded Swift
receive and approved admission/usage controls remain meaningful follow-ups.

### October 30 authorized optimization follow-through

- FastAPI lifespan owns a reusable provider HTTPX client and closes it on shutdown.
  Standalone/provider CLI calls keep transient owned clients. Explicit test
  transports remain isolated; mounted apps without lifespan use safe fallback.
  No response cookies are retained and Authorization stays per request. Standard
  pool limits, model settings, token caps and no-retry behavior are preserved.
- Local HTTP/1.1 probe: two pooled calls used one TCP connection; two standalone
  calls used two. This verifies connection reuse, not live OpenAI TLS latency or
  monetary savings. Lifecycle tests cover errors/cancellation, shutdown and
  concurrent credential/cookie isolation.
- Preview uses runtime-only requirements; full requirements retain tests and
  Apple crypto dependencies. Fresh isolated install, actual launcher and HTTP
  generate/rewrite/422 checks passed with pytest/JWT/cryptography absent.
- CI deduplicates feature push/PR execution by running PRs plus main pushes, with
  manual dispatch for other branches. Pip cache hashes both requirement files.
  YAML/event/cache checks pass; actual remote cache/billing gains unmeasured.

Integrated backend: **374 passed**, one existing deprecation warning; dependency
consistency passes. No Swift source changed in this follow-through (previous shared
suite: 32 pass/1 optional skip). No Xcode/native or real-model acceptance is implied.
No paid inference, quota policy, private caching/storage or campaign migration.

### October 30 keyboard requirement and proposal

Retained the owner's supplied source and updated provisional PRD/roadmap/instructions
so the keyboard is no longer indefinitely deferred. Added `KEYBOARD_PROPOSAL.md`:
reusable architecture, platform/context/privacy constraints, all-hosts-untested
matrix, effort/cost ranges and decisions before implementation. Five official
Apple read attempts returned proxy403; sources are linked but current contracts
were not refreshed. No extension target, app workflow, entitlement, storage or API
changed. This is documentation/proposal work; no native or compatibility tests ran.

### Approved synthetic keyboard feasibility implementation

Implemented an embedded `ProofreadKeyboard` app-extension declaration and UIKit
controller with minimal lowercase typing/switching controls, optional Full Access
status inspection, explicit context capture, local generate/rewrite fixtures and
safe cursor insertion. Shared Foundation model enforces exact bounded snapshots,
document identity comparison, selection blocking, fresh candidate IDs, single-use
selection and invalidation. Only counts are displayed; no host text is saved.
No network, App Group, Keychain/session sharing, backend/schema, personalization,
private-history or paid-service change. Full Access is optional for these fixtures.

Executed: 10 new safety tests (initial missing-model red captured); integrated
shared Swift **43 passed**, no skips/failures, against a real local mock API.
Backend **374 passed**, one existing warning. Extension source/response model
subset type-checks in Foundation; UIKit syntax parses and project/plist references
pass static checks. **UIKit/iOS compilation, XcodeGen generation, keyboard layout,
permissions, insertion and all messaging-app compatibility remain unverified.**
Current Apple source access remains blocked. See `KEYBOARD_PROTOTYPE_TESTING.md`;
this implements the spike's code, not platform acceptance or product completion.

### Observation native-build defect and correction

Owner-supplied Xcode 27.2 build output reached compilation and failed in
`ComposerModel` conditional `@ObservationIgnored` expansion (unexpected getter/init
accessors). This was reproduced with the real Observation macro compiler path on
Linux before changing source. Each ignored property and its attribute now live
inside the same conditional declaration branch. The shared test entrypoint also
forces an Observation typecheck without runtime linking, covering a path previously
excluded on Linux. Compiler regression passes; 42 Swift tests pass with 1 optional
local-API skip. No actual successful native/Xcode build is claimed: owner rerun is
required. A checksum-guarded backup-first patch was tested, including repeat use,
for the supplied source bundle. No backend, keyboard behavior or product scope
changed in this fix.

### Device feedback and scope clarification

Owner reports successful iPhone installation/launch and a connection error in the
standalone app. Current default endpoint is simulator loopback, which points to
the phone on device; a scheme override, if present, must be checked. No server was
deployed by the offline spike. The owner-supplied preceding Mac log showed native
BUILD SUCCEEDED but failed two networking fixture methods (four assertions), so
Mac suite acceptance remains incomplete. See `DEVICE_KEYBOARD_UX_FOLLOWUP.md` for
a feasible in-keyboard flow and unsupported screen-reading/button-injection
constraints. No network/private-data/UX implementation changed in this follow-up.

### Device setup follow-through

Physical-device loopback configuration now reports a setup-specific diagnostic,
without changing HTTPS-only remote endpoint policy or silently falling back to
fixtures. The app displays the actual safe configuration error. Simulator/Linux
loopback development remains allowed. Mac request-fixture inspection now accepts
URLSession's stream-backed body, with bounded stream regression coverage; no
production transport was changed. Observation typecheck passes; shared suite:
46 passed, 1 optional local API skip. Mac/Xcode rerun is still required to accept
these corrections on the owner's toolchain. API credentials remain absent here;
no backend deployment, paid inference, campaign reset or screenshot/context
collection was performed. Screenshot/share OCR is a possible explicit-consent
future workflow, not implemented screen reading.

### Visual context research

Research-only alternative documented in `CONTEXT_CAPTURE_RESEARCH.md`: retain the
keyboard UI but investigate user-authorized screen capture + on-device OCR.
Retrieved maintained API bindings expose iOS27 ScreenCaptureKit availability and
legacy ReplayKit deprecation; owner reports iOS27.0.1. No on-device capture, OCR,
host compatibility or store acceptance is verified. Added a read-only SDK-header
inspection script; Bash syntax passes. Direct Apple/Snap docs were blocked and
secondary bindings are not treated as shipping SDK proof. Capture/privacy
architecture approval is pending; no product behavior or paid calls changed.

### Approved capture/OCR study preparation

Added an explicit-launch-only native Vision self-test using an app-generated
synthetic image, not a screen frame. No capture adapter, audio, image persistence,
network, shared container or AI call was added. Added Foundation session control:
one pending result, fresh session/request tokens, bounded nonblank text, 30-second
expiry, Stop/invalidate and late-result rejection. Native self-test schedules
cleanup and clears state on disappearance/backgrounding; its actual UIKit/Vision
execution is unverified here. Normal launch remains the existing app.

TDD: missing model/types failed first; 8 new control tests pass. Shared suite:
54 passed, 1 optional local-API skip; Observation compiler check passes. Native
source syntax parses, not iOS SDK typechecking. Actual screen-capture/OCR/host
compatibility remains unverified. Need the owner's Mac SDK inspection output to
select/validate modern iOS27 capture APIs; user has approved the narrow study and
need not approve it again. See `LOCAL_CAPTURE_STUDY.md` for exact boundaries.

### iOS27 capture adapter source and standalone test app

Actual owner SDK output resolved the API gate: Xcode27.2 build27B52/iPhoneOS27.2
headers expose modern ScreenCaptureKit; user reports device iOS27.0.1. Added an
explicit system-picker, current-app-only capture study controller, one requested
frame at a time, local Vision OCR, bounded pixels/text, expiry/Stop/background
cleanup and stale-callback guards. Microphone/camera filters are rejected; audio
is disabled; no recording-file output/network/shared container was added. A
standalone `ios/CaptureStudy` target avoids altering the working keyboard signing.
Stop errors block restart rather than assuming OS capture ended; instructions
require system stop/relaunch when uncertain.

Review caught/corrected the capture-button enable condition and Objective-C boolean
getter import names. Static Swift syntax and YAML/source references pass. Shared
Foundation tests: 54 passed, one optional local API skip; Observation compiler
regression passes. **Native capture code has not been compiled against Apple's
SDK or run here.** First device build/capture/OCR remains unverified; no cross-app,
background, Snapchat notification, keyboard-transfer or App Review claim is made.

### Capture SDK compiler corrections from owner's Mac

Owner native build diagnostics identified mutable picker configuration overlay,
`presentForCurrentApplication()` Swift rename and local observer shadowing. Source
now uses var configuration, the reported Swift API name and explicit self property
assignment. A one-frame retained read-only sample wrapper and lock-protected OCR
worker document cross-queue sendability rather than sharing unguarded state. Vision
cancellation occurs outside the lock. The source still requires actual SDK rebuild;
Linux parsing is not native typechecking. Shared suite: 54 passed/1 optional skip.
The shadowing error was reproduced in a compiler snippet before correction. A
checksum-guarded backup-first single-file patch passed apply/repeat/changed-file
refusal checks; it leaves project/signing settings untouched. Completion-handler
APIs remain intentional for late-start/stop tracking; async-alternative suggestions
are not compilation errors. Capture behavior itself remains unverified.

### Capture study clean/retry helper

Owner requested folder cleanup and another run. Added a reversible local Mac helper
that applies only the known corrected controller, backs up source and generated
project-local caches, then compiles unsigned into fresh local DerivedData. It does
not regenerate the Xcode project, overwrite signing settings, remove source or
clear global caches. Failure stops before opening Xcode; logs remain in the backup.
Two offline helper tests verify success/failure status, source/signing preservation
and archived cache content. These are mocked tool checks, not actual Mac builds;
owner must run the helper and report the native result.

### Current-app OCR device evidence and controlled next probe

Owner screenshot displays captured study UI text under the OCR-result heading,
supporting one successful on-phone own-app capture/OCR result. It is output, not
another controls panel. Added clearer output wording and an explicitly confirmed
synthetic Notes switch option, default off. It arms one frame after five seconds,
keeps the original result deadline and avoids the deliberate own-app background
stop only in that explicit mode. No automatic Notes access or cross-app success
is claimed. Match a unique phrase not displayed in the study UI; change it per run
to avoid mistaking self-capture/stale output for success.

New locked one-shot admission gate: 7 new tests; shared suite61passed/1optionalAPI
skip, Observation compiler check passes. Native sources parse; actual new native
build/background capture remains unverified. Callback receipt timing is bounded,
not source-frame age; OS suspension may delay cleanup. User must return promptly,
Stop and verify system sharing ended. No saved recordings, audio, network or AI.

### Owner Mac folder organization helper

Prepared a local organizer for explicitly named prior Proofread demos, ZIPs and
research downloads. It moves them into a dated `Documents/Proofread Archive`,
records paths in MOVED.json, leaves the working capture-study path/source/signing
intact, and installs the Notes updater as a local project tool (without executing
it). START-HERE.txt provides a single run path. No unrelated GitHub/Codex/user
files or broad name-glob matches are moved. Tests verify archival, project/signing
and unrelated-file preservation, plus preflight symlink refusal. Actual Mac
organization is pending owner execution, not claimed performed remotely.

Also corrected the repository cleanup helper to accept its authoritative current
source instead of assuming the earlier fixed controller hash forever. Unknown
source edits still fail closed; tests preserve build failure propagation.
