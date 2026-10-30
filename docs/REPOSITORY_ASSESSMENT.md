# Proofread repository assessment — October 30, 2026

Scope: `codex/evaluation-output-followups` at `3a55e7f2325f9ac0b48812dec4b784d37a012905`, before this documentation-only assessment. This describes the checked-out feature branch, not proof that changes are merged into main. Reviewed documentation, application sources, evaluation tools, tests, scripts and CI; independent backend/AI, evaluation and iOS reviews supplement the coordinator's inspection. No application behavior, dependency, architecture or paid service was changed.

> Follow-up: this is the pre-fix assessment. Subsequent reliability corrections
> and current test results are recorded in `IMPLEMENTATION_STATUS.md`; findings
> here should not be read as claims that those fixes remain unimplemented.

## A. Executive summary

Proofread is a carefully guarded development scaffold for a native communication assistant. It is not yet a personalized communication product. Its strongest implementation is the reliability plumbing: bounded input/output contracts, safe provider failures, cancellation-resistant client state, synthetic authentication tests, and conservative experimental spend controls.

The default path can return three mock replies through FastAPI and the shared Swift client. The mock ignores context when generating and makes punctuation variations when rewriting. An opt-in OpenAI adapter exists but real inference has not been verified. Native SwiftUI compilation and simulator acceptance remain unverified. Style extraction exists as a disconnected utility. Relationship memory, retrieval, learning, sessions and persistence do not exist.

The primary product risk is not insufficient infrastructure: it is lack of evidence that the intended AI behavior works. More mock tests cannot establish authenticity. Prioritize a verified generic baseline and a small approved personalization experiment, alongside actual native build acceptance. Do not add a vector database, fine-tuning or elaborate ranking yet.

Finalized PRD/SPEC/research/roadmap exports are absent (`docs/source/` does not exist). Existing reconstructed documents are provisional; the owner's latest product statement is explicit guidance, not retroactive approval of unbuilt systems.

### Verification in this assessment

- `backend/.venv/bin/python -m pytest -q` from `backend`: **335 passed**, one existing Starlette/httpx deprecation warning.
- `.venv/bin/python -m pip check`: no broken requirements; readonly pip-cache warning is nonfatal.
- Linux Swift 6.1.3 shared suite: **31 tests executed, 30 passed, 1 optional local-server test skipped, 0 failures**. No Xcode or native simulator claim.
- Synthetic probes confirmed HTTP 422 input echo and style-extractor representation limits described below.
- Previous 31/31 local URLSession integration and CI results in status documents are historical evidence, not rerun native acceptance.
- No live AI, private user data, model superiority experiment, fresh vulnerability advisory audit or production deployment was performed. Prior October 15 pricing/audit evidence must not be presented as current certification.

## B. Architecture overview

Current native execution path:

```text
ProofreadApp → ReplyClientConfiguration → ComposerView → ComposerModel
 → ReplyClient.generate → POST /v1/responses → ReplyRequest validation
 → build_provider → MockProvider OR OpenAIProvider
 → candidate/schema validation → ReplyResult → suggestions/copy
```

`ios/Proofread/Models/ComposerModel.swift` owns form validation, loading, error and suggestion state. Input edits invalidate request identity and cancel old work; late completion cannot overwrite new state. `Services/ReplyClient.swift` encodes the contract, sends ephemeral URLSession requests, validates responses and hides raw error payloads. Configuration allows HTTPS or loopback HTTP and rejects URL credentials/query/fragment.

`backend/app/main.py` exposes health and response routes. It constructs a provider for each request; there is no authentication middleware, database, worker, persistent user identity or feedback route. Generated candidate IDs are response-local positions, not persisted message identifiers.

`backend/app/provider.py` separates the mock from a single hosted-model request. The live adapter requests structured JSON, validates three bounded distinct texts, rejects incomplete/refused output, caps completion tokens, applies a total network deadline and response-size bound, and makes no automatic retries. This is generic context-conditioned generation, not personalization. Error handling maps configuration failure to 503 and provider failure to 502.

Disconnected foundations:

- `app/style_profile.py`: computes aggregate lexical/punctuation signals; no request path calls it.
- `app/apple_identity.py`: verifies an identity JWT against public keys; no route consumes the result and no session/nonce issuance/consumption exists.
- `evaluation/`: offline contract reports, blinded review artifacts and vote summaries; a separate gated live runner reserves a one-time budget before inference.
- `tools/preview/`: browser harness mounting the real API with provider forced to mock, loopback binding and no access log. It is not a SwiftUI rendering or approved final design.

No database or ORM is present. PostgreSQL/pgvector and authenticated FastAPI in provisional documentation are proposed future architecture, not current infrastructure.

## C. Implementation status

| Capability | Actual state | Evidence / limitation |
| --- | --- | --- |
| Generate/rewrite request contract | Implemented and tested | FastAPI and Swift fixtures; actual mock HTTP checks historically recorded |
| Contextual mock generation | Mocked | Same three fixed informal replies regardless of incoming message/goal |
| Mock rewriting | Mocked | Draft truncation/punctuation variations; not semantic improvement |
| Real-model generation/rewrite | Implemented adapter, unverified live | Offline transport/contract tests only |
| Swift client/state management | Implemented, shared-source tested | Safe errors, URL checks, stale completion protection |
| Native iOS application | Partial; native acceptance unknown | SwiftUI source and XcodeGen spec; no actual Xcode evidence |
| Style extraction | Implemented but disconnected | Deterministic aggregates, not learned identity or generation context |
| Personalization | Missing | No style input/profile ID in generation request; `personalized:false` |
| Conversation context | Minimal | One incoming message, relationship string, goal, optional draft; no ordered history |
| Relationship awareness | Partial prompt conditioning | Free-text relationship only, no recipient identity/history |
| Candidate ranking | Missing | Provider order retained; labels are not quality scores |
| Copy | Implemented; partial verification | Model lookup tested; actual UIKit pasteboard interaction unverified |
| Editing and feedback learning | Missing | No editable candidate event, chosen/edit feedback route or update loop |
| Apple identity verification | Internal foundation tested | No end-to-end Apple sign-in acceptance or session authorization |
| Persistence/import/retrieval/deletion | Missing | No data layer or private-data lifecycle |
| Quality evaluation | Framework partial | Contract checks and review preferences; no meaningful human results |
| CI | Backend tests only | Python 3.12 GitHub Actions; no native or shared Swift CI |
| Local preview setup | Confirmed unreliable | Python version/recovery issue reproduced by owner; no launcher preflight |

## D. AI intelligence assessment

### Writing style

`extract_style_profile` measures average token count, lowercase first character, emoji/exclamation/question ratios and five common markers from nine hard-coded English slang terms. These are useful transparent descriptive statistics, not an adequate representation of voice. It cannot model syntax, code-switching, humor, register, vocabulary range or intent-dependent style. Runtime type validation also accepts a bare string as a sequence of character examples (`extract_style_profile("hello")`), despite its list annotation. It assigns no confidence or minimum-data threshold and does not distinguish stable preferences from a few unusual examples.

Concrete limits: a quote before a lowercase word produces a zero lowercase-start signal; a keycap emoji is missed by the emoji range and counted as a word. These are representation limitations verified with invented strings, not proof the entire utility is broken. Changing profile semantics requires owner approval under the latest policy.

Most importantly, none of these signals affect generated replies. The system currently cannot overfit style in generation because it never receives style; it also cannot personalize at all.

### Context and relationship

`OpenAIProvider.build_payload` includes the current incoming message, relationship, goal and optional draft. This gives a generic model enough input for simple contextual replies, in principle. There is no history, role attribution, previous commitments, uncertainty/conflict handling or recipient-specific evidence. Sarcasm and implicit intent depend entirely on the underlying model and sparse input, and have not been evaluated.

JSON packaging and instructions to treat messages as data are helpful prompt hygiene, not a proven injection defense. Offline tests prove payload construction and schema handling; they do not prove the model resists instructions embedded in conversations.

### Response usefulness and diversity

Normalization rejects case/whitespace duplicate texts, not semantically equivalent suggestions. Three punctuation variations can pass. Fixed Natural/Direct/Playful labels can encourage inappropriate playfulness in serious contexts; label suitability needs experiments before changing the product contract. The mock's casual responses should never be used as evidence that formal, sensitive or ambiguous cases work.

Intent preservation is a system instruction, not a verified semantic guarantee. Structural validation cannot detect invented facts, reversed commitments, unwanted intimacy or meaning loss. A long mock draft is truncated to the output limit, so it explicitly cannot establish full intent preservation.

### Learning and measurement

No examples, selections or edits are retained; no recipient memory or profile updater exists. This protects against premature retention but does not deliver continuous learning. Evaluation uses eight public synthetic scenarios with only three preference dimensions (authenticity, helpfulness, intent preservation). It lacks dedicated ratings for relationship appropriateness, candidate diversity, uncertainty, editing effort and disaggregated user/recipient outcomes. These are recommended additions, not fabricated existing metrics.

Recommended research progression: generic baseline → explicitly supplied short style guidance/examples → structured profile only if it adds measurable value → relationship-specific examples → retrieval only if the simpler context fails. Use synthetic data first; consent and isolation before real-user examples. Do not assume larger models or more prompt stages solve the issue.

## E. Code quality and engineering assessment

### Strengths worth preserving

Small modular implementation; no unnecessary service fleet. Tests cover provider malformed output, Unicode bounds, accounting, unknown outcomes, cancellation races and JWT attacks. Mock defaults and blocked real transports make CI safe. The provider avoids automatic retry spend. The Apple verifier fixes issuer/key URLs, algorithms and audience and bounds fetch/cache behavior; it is appropriately described as internal. Evaluation artifacts avoid overwrites and distinguish missing ratings from failures. Swift avoids showing private server error payloads.

### Confirmed defects and material gaps

1. **Preview setup failure (high practical impact).** `tools/preview/start.command:4–6` checks only whether an executable exists. It can create/reuse Python 3.9 and then crash on modern annotations; an interrupted installation leaves an executable environment that subsequent runs skip repairing. This matches the owner's terminal evidence. Fix by validating supported interpreter versions, checking an existing environment, providing an explicit interpreter override, and verifying dependencies before claiming readiness. Do not delete existing environments automatically. The recent 3.15 install has not been validated as compatible.
2. **Validation error input echo (privacy hardening needed).** `backend/app/main.py:9–22` uses default FastAPI validation errors. A synthetic oversized goal returned the submitted goal in HTTP 422 `detail[].input`; model-level errors can include request context. This is returned to the requester, not evidence of an external leak or logging today, but it creates avoidable exposure in future client diagnostics/proxies. Redact validation payloads while retaining status and field locations; regression-test privacy.
3. **No production abuse/cost perimeter.** `/v1/responses` has neither authentication nor per-user quotas, body-size middleware or concurrency limits. Field bounds apply after request-body decoding. If deployed with live credentials, callers could consume repeated inference despite per-call token bounds. The one-time evaluation ledger protects its CLI only; ordinary API generation does not use it. Keep the service local/mock until a reviewed perimeter exists.
4. **Swift fetch is unbounded before validation.** `ReplyClient.swift:26` buffers the full response with `session.data(for:)`; text limits are checked afterward. A bad endpoint/intermediary could send an oversized body. Add a bounded fetch mechanism with cancellation and test it; this does not require changing the app workflow.
5. **Dependency/install reproducibility.** Broad requirements ranges and no resolved lock mean the Mac and cloud can install different versions. Test tools are mixed with runtime packages, making preview installation larger. CI tests one Python version, not every version README's “3.11+” may imply. Recommend an explicitly supported version matrix and reproducible dependency constraints before releases. No fresh advisory audit was run here.
6. **Native/CI acceptance gap.** Only backend tests run automatically. Shared Swift Linux tests cannot compile Apple's Observation adapter, SwiftUI bindings, entitlements or UIKit copy. Add native build acceptance after a local Mac or approved runner is available; no build can be claimed from source inspection.
7. **Documentation/checkpoint drift.** Status/next-task files contain appended historical counts and repeated gates (327, 330, 331, 335) rather than a compact current snapshot. This makes handoffs harder. Consolidate after this assessment while preserving dated evidence. Profile/auth wording must continue distinguishing library existence from user-facing integration.

8. **Unicode contract disagreement (reproduced).** Backend distinctness accepts precomposed `café` and decomposed `café` as separate strings, while Swift's canonically equivalent string comparison rejects the same successful payload. Align normalization and add cross-language fixtures; do not treat this as a semantic-diversity solution.
9. **Apple key decompression defeats the intended allocation bound (reproduced).** `apple_identity.py:153–163` checks bytes yielded after HTTPX decoding. A synthetic compressed response of 2,068 bytes expanded to 2 MiB before the 64 KiB consumer check rejected it. The verifier still fails safely, but the documented body cap is not a decompression memory cap. Request/check identity encoding or explicitly bound decoding before acceptance.
10. **Provider exception chains retain content (reproduced).** `provider.py:197–198` uses `raise ... from exc`; formatting a Pydantic validation traceback includes a synthetic candidate snippet. Current HTTP 502 output is safe and no traceback logger exists here, so this is a future diagnostic exposure risk, not proof of a logged leak. Suppress private validation context at the trust boundary and test formatted diagnostics.
11. **Live preflight lacks resource bounds (reproduced).** `evaluation/live.py:227–234` eagerly buffers the model-availability response with phase-only timeouts. A controlled transport returned over 2 MiB before rejection. Add total deadline/stream bounds to this GET as well; no paid request or ledger write occurred in the probe.
12. **Live-to-review integration is incomplete.** The two-case live output is not the eight-case `_Report` accepted by `runner.verify_report`, so actual live output cannot directly enter `compare`/`summarize`. Introduce an explicitly compatible review path without dropping failed/unrun cases or silently expanding the approved two calls. The generic report also lacks exact prompt/config/code revision and usage manifest; preserve those before meaningful experimental comparison.

No blanket security certification is implied. No persistence is a current minimization benefit, not a completed privacy architecture. Model-provider data handling, retention policy and operational diagnostics still require review before real conversations.

## F. Product experience assessment

The harness lets users express relationship and goal and obtain/copy suggestions. State invalidation is thoughtful and avoids copying suggestions from an obsolete request. However, the default experience cannot demonstrate the product's core value: generate ignores user input, rewrite is cosmetic, no personal voice is applied and users cannot teach the system through edits.

A fixed Playful option is not universally appropriate. A single incoming-message field cannot resolve every ambiguous conversation. There is no onboarding/profile editing, history import, relationship management, consent/deletion flow, per-candidate edit submission or progress toward learning. These are missing workflows, not reasons to invent new navigation without approval.

The repeated Python setup failures show that even demo access is currently too costly for a founder. The immediate correction is reliable launcher preflight and a supported installation path, not another simulated product screen. A future preview should make mock/live and personalized/unpersonalized state explicit without overloading the actual native UX with engineering details.

## G. Prioritized improvements

| Priority | Current limitation / why it matters | Proposed improvement and expected benefit | Complexity / trade-off |
| --- | --- | --- | --- |
| Critical before external/live use | Unauthenticated repeated calls can incur cost; no private-data lifecycle | Keep local/mock; review auth, quotas and storage boundary before deployment | Medium–high; delays real-user trial but prevents uncontrolled exposure/spend |
| High, immediate | Founder cannot reliably launch preview | Interpreter/version/dependency preflight and recovery tests | Low; support a smaller explicit Python set rather than promising every version |
| High, immediate | 422 can repeat private input | Safe field-level errors without submitted values | Low; less detailed diagnostics, better minimization |
| High, evidence | Live adapter only tested against invented completions | Execute already bounded synthetic generate/rewrite check once prerequisites pass | Low engineering; external credentials, updated evidence and valid ledger required; proves compatibility only |
| High, evidence | Native app never built | Unsigned Xcode build, then simulator workflows on actual Mac | Low–medium; local setup or approved runner cost |
| High, approval | No personalization reaches generation | Compare generic vs explicitly supplied style examples/guidance in isolated synthetic experiment | Medium; approval required; can increase tokens and imitation errors; no learning claim |
| High, approval | Sparse immediate context | Small bounded conversation-turn context with clear speaker attribution | Medium; API/UI semantics and privacy need approval |
| Medium | Structural diversity does not establish useful alternatives | Human diversity/relationship/intent rubric and adversarial scenarios; rank only after evidence | Medium; review effort; avoid brittle semantic heuristics |
| Medium | Hand-maintained test environments drift | Supported Python/Swift versions, dependency reproducibility, Swift CI | Medium; maintenance and CI resources |
| Medium | Overbroad error/data surfaces | Bounded Swift receive and payload-free operational metrics | Medium; extra networking code; logging policy must minimize content |
| Long term, conditional | No relationship memory or learning | Approved editable profiles and event feedback; scoped retrieval only when measurable | High; retention/isolation and stale-memory risks |
| Long term, conditional | No evidence for expensive optimization | Benchmark cost/latency before caching, ranking passes, embeddings or fine-tuning | Variable; premature optimization may reduce reliability |

## H. Major decisions requiring owner input

The most useful next architecture decision is approval or rejection of decision 1; decisions about persistent memory need not be forced before evidence. These are proposals, not implementation authorization. Routine confirmed-defect fixes can proceed separately after delivery of this assessment.

1. **First personalization experiment.** Alternatives: explicit style guidance/examples; structured profile first; retrieval first. Recommend explicitly supplied synthetic examples/guidance versus the same generic baseline, entirely in memory, with no private data. Benefit: shortest experiment that tests voice conditioning. Cost: more input tokens and possible over-imitation; medium effort. Profile semantics and any broader paid evaluation require separate approval.
2. **Conversation context contract.** Alternatives: retain one message; accept bounded speaker-attributed recent turns; ingest full history. Recommend bounded recent turns before retrieval, after reconciling originals. Better intent interpretation, but changes API/input UX and handling of other people's text. Medium effort and prompt-injection surface.
3. **Identity/session and data lifecycle.** Alternatives: ephemeral no-storage use; approved Apple sessions plus minimal editable profiles; raw-history-first storage. Recommend ephemeral experiments now, then Apple sessions and minimal data after a concrete consent/retention/deletion/isolation design. High effort; approval of a verifier is not approval of sessions/storage.
4. **Candidate behavior.** Alternatives: retain fixed Natural/Direct/Playful; context-appropriate intent-preserving alternatives; configurable tones. Recommend evaluate context-appropriate alternatives before any workflow/schema change. Potentially improves sensitive-context usefulness; risks losing predictable option labels; medium effort.
5. **Quality acceptance and evaluation budget.** Alternatives: informal founder preference; fixed rubric and independent blinded comparisons; automated model judge alone. Recommend human-primary authenticity/intent/relationship/diversity judgments with tie/missing outcomes, multiple scenarios and uncertainty, plus editing effort. No arbitrary superiority threshold is adopted. Define target population and decision threshold together before expanded paid runs; current $2 approval is only a compatibility check.
6. **One-time campaign continuity (current blocker).** Read-only inspection found the preserved ledger still reports available/zero reserved, but its runtime fingerprint differs from this machine. `reserve_once` therefore correctly blocks it; October 15 model evidence is also stale. Alternatives: defer paid testing, or explicitly authorize a reviewed migration of this same campaign with preserved accounting and no added allowance. Recommend defer calls until a migration procedure and the recorded no-spend evidence are reviewed. Do not reset/recreate/rebind implicitly. This is a safety-design trade-off, not permission to issue fresh credit.
7. **Native verification execution.** Alternatives: user's local Mac; existing no-new-cost Mac runner; new paid hosted runner. Recommend local unsigned build first. A hosted runner needs quota/cost approval; App Store/device signing is a later gate.
8. **MVP reconciliation and release boundary.** Confirm any material conflicts once finalized exports arrive; decide approved screens, import scope and private-beta acceptance before those features. Keep native SwiftUI and current provider/framework while gathering evidence; no replacement is currently justified. Protected-branch merge/release still requires explicit authorization.

## I. Proposed development roadmap

| Phase | Work | Dependencies | Measurable exit |
| --- | --- | --- | --- |
| 1: recover access and fix confirmed reliability issues | Launcher/version handling, sanitized validation errors, current checkpoint consolidation | Routine fixes; synthetic data only | Regression tests fail before fixes and pass after; founder launches preview successfully |
| 2: verify real vertical slice | Same-day model evidence/key/ledger checks; bounded synthetic generate+rewrite; native app build and simulator copy/error flows | Secure key, refreshed evidence, explicitly resolved campaign runtime mismatch, Mac/Xcode | Actual outputs/usage/latency/cost recorded; actual Xcode result; no false quality claim |
| 3: demonstrate voice conditioning | Generic vs minimal explicit-style experiment and richer rubric | Owner approval, originals as available, separate spend authorization if needed | Blinded results with failures/ties/limitations and edit effort; decision whether profile complexity is justified |
| 4: secure identity and minimal memory | Session/nonce flow, user isolation, consent, deletion, approved editable profile | Approved architecture/privacy and verified Apple compatibility | Negative auth/replay/isolation tests; deletion lifecycle verified before private history |
| 5: approved contextual workflows | Bounded turns, relationship-specific data and feedback; retrieval only if justified | Approved UX/context/data design and quality evidence | End-to-end native workflows plus measured relevance/authenticity outcomes; no cross-user retrieval |
| 6: beta readiness | Accessibility, load/abuse bounds, privacy review, dependency/release checks | Earlier gates; explicit release approval | Documented security, cost, p95 latency and human-quality criteria met on real platform |

The sequence deliberately separates integration evidence, product-quality evidence and production readiness. Passing any one gate does not imply the others.
