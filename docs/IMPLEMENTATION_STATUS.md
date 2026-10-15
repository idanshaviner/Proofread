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
- SwiftUI harness retains generate/rewrite/copy flows. Shared Foundation networking now supports injected ephemeral URLSession, configurable backend endpoint, safe actionable errors, timeout/cancellation and response validation. No significant UI redesign.
- Dependency-free Swift Package compiles the same models/client/configuration as the iOS app, with Python-verified synthetic wire fixtures and an opt-in real URLSession integration check against the mock backend.
- Signed official Swift 6.1.3 toolchain installed for Linux shared-source validation, with repeatable signature-verifying installation and writable-cache test scripts.
- Deterministic aggregate style extraction exists with synthetic tests. It remains disconnected from generation and persistence.
- Offline evaluation CLI runs four invented generate/rewrite cases, records contract outcomes/provenance/latency and prepares blinded human-review templates with a separate answer key. Report imports validate schema, integrity, dataset identity and outcome counts. Quality is explicitly unmeasured; no superiority claim.
- Separate live-integration runner supports the owner's one-time $2 `gpt-5.4-mini` authorization, up to two synthetic generate/rewrite calls, strict evidence/key/availability prerequisites, durable reservations before inference, usage accounting and explicit unrun cases. It stops on unknown outcomes and never refunds or retries. No verified real pricing/capability artifact is available, so paid execution remains blocked.
- Backend tests isolate provider environment variables and block live HTTP transports. Existing GitHub workflow explicitly selects mock mode.
- Root `AGENTS.md` now contains the owner's permanent Autonomous Engineering Operating Protocol, linked to `ENGINEERING_PROTOCOL.md` and durable `NEXT_TASKS.md`. Work proceeds on feature branches with validated commits and PR review; consequential uncertainty prompts questions throughout development.
- Resumed offline implementation: completed review validation and preference summaries with blinded or validated-key unblinded counts, missing/unrated/excluded outcomes distinct, and no quality claims. Fixed shared review/source references and ordinary paired-artifact write failures, with regression coverage written before fixes.

## Verification in this cloud instance

- Baseline: 14 backend tests passed on Python 3.12.14 when run from `backend`, as required by `AGENTS.md`. An initial invocation from the repository root failed imports; this was a working-directory error, not a product defect.
- Latest backend: **206 passed**, no failures or skips, on Python 3.12.14, including 27 live-runner control tests with mocked HTTP and 54 new review/CLI/artifact regressions. One nonfatal Starlette TestClient/httpx deprecation warning. Dependency consistency previously passed; dependencies did not change. Tests previously also passed with `PROOFREAD_PROVIDER=openai` inherited externally, proving the test environment overrides it safely.
- Shared Swift networking/configuration: **14 passed, no skips or failures** with actual Swift URLSession calls to a fresh local mock backend for generate, rewrite and HTTP 422. With integration disabled: **13 passed, 1 explicitly skipped**. Swift 6.1.3 on Linux compiled the same Foundation sources used by the app; no SwiftUI, Xcode or simulator validation is implied.
- Swift installer signature/fingerprint verification and repeat execution succeeded without a second download. Both helper scripts passed shell syntax checks.
- Fresh FastAPI HTTP checks passed for health, generate, rewrite, punctuation-only rewrite, 10,000-character rewrite and missing-draft HTTP 422.
- Evaluation CLI run/compare commands executed with synthetic data: four contract passes and four blind-review cases. Reports and case counts were checked. These commands do not run live inference or establish quality.
- Actual offline CLI run → compare → invented ratings → summarize passed for four cases with validated unblinding. Ratings in this smoke test are fabricated acceptance-test data, not human quality evidence. Existing output preservation, changed material rejection and paired-write rollback have targeted tests.
- Canonical one-time approval ledger initialized once at `/workspace/.proofread/live-budget.json`, outside Git: available, zero calls reserved, **$0 paid expenditure**. Actual default live CLI invocation was blocked without changing that ledger. Both credential variable names remain unset. The ledger is bound to this runtime and cannot authorize a copied/rebooted campaign; cross-instance spending requires stronger coordination, not reinitialization.
- GitHub API access recovered after earlier HTTP 403 responses: the backend workflow for original `main` commit `15169a6` is verified successful. Feature-branch CI is a separate check. OpenAI documentation previously returned HTTP 403; current model-specific compatibility remains unverified.

## Outstanding gates

- **Live model behavior:** the owner approved `gpt-5.4-mini` with a one-time $2 maximum. Secure credentials and current verified pricing/context-window/structured-output evidence remain unavailable. The bounded runner has offline control tests; no paid calls have run. All provider tests use mocked transports.
- **Native app:** no Xcode, simulator, device, signing or SwiftUI compilation ran here. Run XcodeGen and actual Xcode build/acceptance on macOS. Linux Foundation tests cannot satisfy this gate.
- **Privacy and identity:** authentication, consent/deletion flows, persistence and tenant isolation remain unimplemented. Do not store or import private conversations. Sign in with Apple and database choices remain provisional.
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
