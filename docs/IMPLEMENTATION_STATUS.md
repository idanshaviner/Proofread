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
