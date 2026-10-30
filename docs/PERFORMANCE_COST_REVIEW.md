# Performance and cost review — October 30, 2026

Review baseline: audit-reliability commit `ca0fe8a`. Reviewed backend request/provider
and Apple verification paths, Swift client/composer, browser preview, evaluation
and budget tools, dependency setup and GitHub Actions. This is a bounded review,
not a proof that every possible optimization has been found.

## Implemented low-risk CI improvements

- `actions/setup-python` pip cache keyed by `backend/requirements.txt`: reuses
  downloaded/built packages on later compatible runs. A miss remains a normal
  install; the cache is not a lockfile or permission to cache secrets.
- Cancel superseded runs for the same workflow event/ref. The workflow is
  mock-only, so cancellation cannot abandon paid inference accounting. Separate
  push/PR groups preserve both current checks; they still duplicate some work.
- Explicit `contents: read` workflow permissions.

YAML parsed and configuration checked locally; backend tests: 364 passed, one
existing deprecation warning. Remote Actions cache hit rate, runtime and billing
savings have not been measured. Do not claim a percentage improvement.

## Swift input-validation optimization

Reject over-limit text using at most `maximum + 1` Unicode scalars before running
whitespace trimming. This keeps the same codepoint limits and nonblank rules while
avoiding whole-string work for enormous invalid pastes. Normal-sized input still
uses the existing whitespace semantics. Local synthetic performance evidence and
shared-suite verification are recorded in implementation status; Apple UI timing
remains unmeasured. A Linux Swift 6.1.3 `-O` prototype comparison measured roughly
25.9 ms → 0.067 ms per one-million-scalar invalid check. Valid maximum-length
ASCII checks measured roughly 0.512 ms → 0.580 ms: bounded-prefix checking adds
small normal-input overhead. This targets pathological input stalls, not universal
speed improvement; timing is synthetic and not an iPhone benchmark.

## Highest-impact remaining opportunities

| Opportunity | Current behavior | Recommendation / trade-off |
| --- | --- | --- |
| API aggregate spend protection | Per-call token/time caps, but no user quota, auth, global spend or concurrency perimeter; CLI ledger protects only that experiment | Before exposing live API, approve identity/quota/concurrency policies. This matters more financially than micro-optimizing JSON. A semaphore limits simultaneous work, not total spend. |
| Reuse outbound HTTP connections | Each generation creates/closes an HTTPX client; even reusing a provider alone does not pool sockets | Introduce application-lifespan-managed client injection and deterministic shutdown, preserve explicit offline transports and cancellation. Benchmark with a controlled endpoint before claiming TLS/network latency savings. No private response cache needed. |
| Prompt/input budgets | Generate forwards the optional draft even though the native app omits it; field limits are characters, not tokens; no ordered-history budget | Clarify mode semantics before dropping supplied draft data. Add measured token/context budgeting when approved context/personalization is introduced; retain prompt-injection separation. No arbitrary input truncation that may lose meaning. |
| Completion cap and model choice | 2048 default output tokens; controlled campaign uses 512 | Measure completion/reasoning usage and truncation for both modes before lowering caps. A cap bounds maximum output, not actual spend. Keep approved provider/model; cheaper substitutions require approval and quality evidence. |
| Duplicate CI events | Push and pull_request can test the same commit separately | Consider branch/event policy deliberately, preserving required checks and merge-queue needs. Current concurrency only cancels stale same-event work; it does not eliminate push/PR duplication. |
| Preview installation footprint | Full requirements include pytest, JWT and cryptography even though preview generation uses neither auth verifier nor tests | Split runtime/dev/optional auth dependencies and reproducible constraints in a follow-up. Keep CI installing the complete suite; avoid breaking the self-contained preview or weakening crypto floors. |
| Swift response memory | URLSession buffers body before candidate limits are checked | Bounded receiving/cancellation remains a reliability and memory priority. Test actual stream limits and injected session behavior on shared Swift and Apple targets. |
| Measurement | No production latency percentiles or cost-per-success data | Add payload-free timings/counts/usage after logging/privacy review. Track contract failures, truncation, unknown outcomes and retries separately. No raw message or candidate logging. |

## Existing choices that already contain cost or work

- One model request produces three suggestions; no three-call fan-out or model
  judge/ranking pass. Preserve this until measured quality justifies extra work.
- No automatic provider retries, embedding infrastructure, fine-tuning, scheduled
  imports, database or background paid jobs.
- Composer blocks double-submit and cancels/invalidates obsolete requests, including
  cancellation before task entry. Browser also aborts outdated fetches. A client
  abort does not guarantee cancellation or nonbilling of upstream inference.
- Provider/network/key/preflight timeouts and byte limits prevent prolonged work
  and oversized responses; they do not replace aggregate quotas.
- Apple single-flight cache and refresh cooldown reduce repeated key fetches when
  a verifier is reused correctly. Per-request verifier construction defeats this;
  distributed caching is unnecessary at the current scale.
- Mock-only default development/CI/preview incurs no model inference charges.
- Swift package has no external dependencies and retains local build caches.

## Avoid premature or risky 'optimizations'

Do not cache private replies/history without an approved retention/isolation and
invalidation policy. Repeated requests may have different intent even with similar
text. Do not reduce candidate count, quality, context or privacy guarantees to
claim savings. Do not remove file fsync/locking from one-time accounting: durability
is more valuable than shaving milliseconds from a two-call experiment. Do not
renew/reset the campaign to benchmark model performance.

## Local measurement and limits

100 preparations of blinded comparisons for the current eight-case synthetic
reports: median **0.475 ms**, maximum **0.770 ms** on this instance using
`time.perf_counter`. This includes repeated dataset validation/hash work. It is a
small local CPU measurement, not end-to-end inference latency or a stable cross-
machine benchmark. No cache/refactor is justified for this path at current scale.

Additional offline probes: two sequential calls on one OpenAIProvider created and
closed two HTTPX clients; provider reuse alone will not preserve connection pools.
A valid generate request carrying an optional 10,000-character draft forwarded
roughly 10,000 extra bytes upstream. A synthetic 20-request API burst admitted 20
concurrent generations without authentication. None used a real model. These
confirm mechanisms, not billed costs or production throughput.

A maximum 500-example style batch (5,000 characters each) took roughly 0.468 s
and 21.62 MiB traced peak in an independent local synthetic probe. This utility
is disconnected from interactive generation, so prioritize actual request latency
first. A streaming aggregate implementation could reduce temporary token lists
without changing profile meaning, but profile semantics themselves remain gated.

No paid requests, official price refresh, network/TLS benchmark, Apple platform
profiling or billing analysis was performed. October 15 pricing is historical and
must be refreshed before live testing. The preserved campaign runtime mismatch
continues to block paid execution. Recommend finishing reliability/measurement
and real baseline validation before pursuing complex cost optimizations.
