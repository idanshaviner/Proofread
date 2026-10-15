# Offline evaluation foundation

Run from `backend` using the development virtual environment:

```bash
.venv/bin/python -m evaluation run --output /tmp/proofread-eval.json
.venv/bin/python -m pytest -q tests/test_evaluation.py
```

This CLI always uses the fixed mock, even if `PROOFREAD_PROVIDER=openai` is set.
It makes no network requests, requires no credentials, and incurs no inference
charges. Cases, incoming messages, drafts and style examples are entirely invented.
Do not replace them with private conversations. Files are created only at the
explicit output paths and existing files are never overwritten.

Dataset `synthetic-v2` has eight cases: four unchanged public baseline scenarios
and four public evaluation-only stress scenarios, with both modes in each split.
Stress cases cover quoted-instruction injection and contextual/conditional intent.
They are not sealed or statistically independent holdouts; do not tune against
them. Review voice examples must not duplicate incoming messages/drafts. The
generic runner does not send those examples to the provider. The version/hash
change invalidates old v1 reports; regenerate report/review/key sets together.

Reports identify the adapter, mock provenance, optional model identity, dataset
version, dataset digest, per-case measured latency and contract outcomes. Dataset
and report SHA-256 digests detect accidental changes and mismatched comparisons;
they are not signatures or proof of provenance. Latency includes local validation
and is not a hosted-model benchmark. Actual latency varies between runs.
Imported reports must also satisfy the versioned schema, candidate contract,
complete dataset case IDs, and counts reconciled against individual records.

`evaluate(provider, system_name, model)` can be reused by a later explicitly
authorized experiment with another adapter. Record exact model/configuration in
the system name/model fields. The current generic runner passes only each API
request; synthetic style examples are human review context and do not personalize
generation. This module does not add a personalized API or history storage.

`contract_pass` means the existing `ReplyResponse` schema accepted an answer.
`contract_failure` means an adapter returned an invalid answer; `provider_failure`
means it raised `ProviderFailure`. The current hosted adapter also wraps upstream
schema failures as `ProviderFailure`, so that status cannot reliably distinguish
network failures from malformed model output. Unexpected programming exceptions
abort the run rather than being hidden as a successful evaluation.

Contract checks do not establish helpfulness, intent fidelity, authenticity or
personalization gains. All quality fields remain unmeasured. The mock ignores
context and its valid output can be inappropriate. No automated quality score or
authenticity superiority claim is produced.

To rehearse a blind human comparison, create two reports, then:

```bash
.venv/bin/python -m evaluation compare /tmp/left.json /tmp/right.json \
  --output /tmp/review.json --key /tmp/review-key.json --seed 42
```

Share only the review file with reviewers. The separate key maps randomly ordered
A/B options to systems and report digests. Ordering is reproducible for the same
reports and seed. Failed cases are excluded and recorded in the key, never counted
as semantic losses. For each case, reviewers can record `A`, `B` or `tie` separately
for authenticity (fit to invented style examples), helpfulness (fit to goal), and
intent preservation (especially for rewrites), plus explanatory notes. This is a
template, not a validated rating instrument or statistical comparison. Mock text
may be recognizable, so mock comparisons are workflow rehearsals only. Establish
a held-out dataset, agreed rubric, multiple independent raters, and uncertainty
reporting before drawing product conclusions. Real-user authenticity evaluation
requires consent and the still-unimplemented privacy controls.

The compare command creates both paths exclusively before writing and rolls back
its own files on ordinary creation/write failures, preserving observed user
replacements. It cannot provide a crash-atomic transaction across two paths:
abrupt interruption may leave partial artifacts. Validate a recovered pair
against the original reports before use; retry with fresh paths rather than
overwriting or blindly deleting existing files. Concurrent adversarial directory
renames are outside this local helper's guarantees.

## Validate and summarize human ratings

After reviewers fill only each case's `preferences` (`A`, `B`, `tie`, or `null`)
and optional text `notes`, validate and count the results against the original
reports and the same comparison seed:

```bash
.venv/bin/python -m evaluation summarize /tmp/review.json /tmp/left.json /tmp/right.json \
  --seed 42 --output /tmp/summary.json
```

This keeps counts blinded. Add `--key /tmp/review-key.json` to validate the exact
regenerated key and include left/right system preference counts. An explicitly
supplied null or malformed key is rejected. The command rejects altered prompts,
candidate options, case identities/order, dataset, extra fields or invalid votes.
It never overwrites an existing summary. Notes and candidate text are omitted
from summaries; report/review digests support reproducibility, not signatures or
proof of reviewer identity. A sheet containing identical candidate content cannot
by itself distinguish otherwise identical source runs; the validated key anchors
the supplied original report digests.

Each dimension reports A/B/tie/missing counts. Empty comparisons, unrated reviews,
partially rated reviews and complete ratings have distinct statuses. Excluded
contract/provider failures are counted separately, not as losses. These are
descriptive counts for one review sheet, not an agreed evaluation instrument,
statistical significance, independent-rater consensus or evidence that personalized
responses outperform generic AI. No inference or private conversation collection
is needed. Prepared Python review/key objects are detached copies of source
reports so editing artifacts cannot silently corrupt the originals.

## One-time live integration scaffold (blocked by default)

`python -m evaluation.live` is separate from the offline CLI. It is limited to the
owner's October 15, 2026 approval: one campaign, up to two synthetic calls (one
generate, one rewrite), model `gpt-5.4-mini`, maximum $2 total, output cap 512 tokens, and the
default service tier. It does not assess personalization. **No real pricing or
compatibility artifact is committed, and no live call has been verified.**

Execution requires all of the following:

- Explicit `--execute` and an exclusive writable `--output` path reserved before
  any requests. Existing output is never overwritten. Blocked results are saved
  as a safe status; raw HTTP responses, keys, and errors are omitted.
- Secure environment key `PROOFREAD_OPENAI_API_KEY` (legacy `OPENAI_API_KEY` also
  accepted). Configure values through environment settings, never CLI or files.
- `--reviewed-spec PATH`: a same-day engineer-reviewed official evidence artifact
  satisfying `VerifiedModelSpec` in `live.py`. It must name the approved model,
  official source URLs, reviewer/date, full context maximum, maximum input/output
  prices per million across **all** applicable pricing/input-length tiers, verified
  response model IDs/snapshots, structured-schema support, default-tier support,
  and proof that `max_completion_tokens` caps **all billed output**, including
  reasoning. Rates must not assume caching, batch discounts or low-length tiers.
  Artifact fields are attestations, not automatic verification of source content.
  Missing/unknown facts block execution. Test fixtures use invented numbers and
  are never a real specification.
- The canonical ledger `/workspace/.proofread/live-budget.json` provisioned once
  by the campaign owner using `initialize_approval_ledger()`. Installation,
  startup and CLI **never** initialize, reset or replace a missing ledger. Do not
  recreate, fork or copy it to mint another allowance. No reset/init/path-override
  CLI exists. Missing, unreadable, reserved, changed or copied-instance ledgers
  block paid execution.
- A nonbillable authenticated model-availability GET succeeds. This establishes
  access only; compatibility still requires the reviewed evidence.

The reservation per call is `(full_context_max * max_input_price + 512 *
max_output_price) / 1_000_000`. The full-context bound includes input framing and
schema tokens without assuming an unverified tokenizer. Output is additionally
reserved even if it shares the context window. If **both** conservative
reservations exceed $2, the run is blocked; small prompt size never relaxes the
bound. Unknown pricing or output-cap semantics must not be filled with guesses.

Before the first paid POST, both calls are durably reserved together under a
local file lock. Reservations are never refunded after failures, crashes, missing
usage or uncertain outcomes. No automatic retries occur. Validated usage, measured
latency, contract/distinctness results, responses and safe failure statuses are
preserved in the ledger after each result before another call. Unexpected usage
beyond bounds, an unverified response model, or nondefault/missing returned service
tier stops the second call. Any provider failure or unknown accounting also stops
the run, since malformed output may hide model/tier evidence. Remaining cases are
explicitly marked unrun; reservations are retained. Contextual relevance remains
human review required.

The ledger binds to hostname and boot identity. Linux execution and lock behavior
are tested here; the macOS `kern.bootsessionuuid` path is covered with a mock,
**not executed on macOS**. Reboot/runtime replacement blocks the existing campaign
rather than issuing fresh credit. Local file locks cannot coordinate spending
across machines. Cross-instance concurrent execution requires a shared spending
coordinator or hard service-side cap and is outside this runner's authorization.
The ledger is a cooperative local guard, not a tamper-proof billing system.

Offline validation: `.venv/bin/python -m pytest -q tests/test_live_evaluation.py`.
All test traffic uses `httpx.MockTransport`; tests do not initialize the canonical
ledger or contact OpenAI.
