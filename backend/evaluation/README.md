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
