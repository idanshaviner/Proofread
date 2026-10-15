# AI evaluation policy and workflow

Personalization is an experimental objective, not a verified capability. Current generation defaults to fixed, nonpersonalized mock responses. Style extraction is local and disconnected from generation/storage. Finalized architecture research is still expected in `docs/source/`.

## Evidence ladder

1. **Contract checks:** schema, exactly three distinct nonblank bounded candidates, provider/errors and safe output handling. They cannot establish contextual relevance, intent fidelity or authentic style.
2. **Generic baseline:** record exact model, prompt/configuration, dataset/version, latency, token usage, errors and cost. Validate live provider compatibility before claiming real-model behavior works.
3. **Personalized comparisons:** compare the same held-out scenarios against generic, explicit style instructions, structured profile and only then authorized contextual retrieval. Keep development/tuning examples separate from evaluation examples; no private data without tested identity, consent, deletion and isolation.
4. **Human assessment:** blinded comparisons for authenticity, intent preservation, contextual relevance, naturalness, usefulness, diversity, preference and editing effort. Agree rubrics and use independent raters/uncertainty reporting before product conclusions. Small synthetic rehearsals do not establish superiority.

Avoid expensive orchestration, vector infrastructure or fine-tuning without measured benefit. Record negative and noisy results. Do not rank systems by schema success alone or turn excluded failures/missing ratings into preference losses.

## Current offline tools

From `backend`, use `.venv/bin/python -m evaluation run`, `compare` and `summarize`, with the exact commands in [the evaluation README](../backend/evaluation/README.md). The CLI uses MockProvider directly regardless of provider environment variables. Committed cases are invented.

Reports carry dataset/system identity, integrity digests, contract outcomes and measured local latency. Review sheets support A/B/tie/null preferences; only votes and text notes may be edited. Summaries verify supplied original reports/content and optional unblinding key, separate missing/unrated/excluded cases and omit raw notes/candidate text. Digests detect accidental changes, not reviewer identity or cryptographic provenance. No human-quality evidence has been collected by the synthetic CLI smoke checks.

Dataset `synthetic-v2` contains the original four public baseline cases plus four public evaluation-only stress cases, balanced across generate/rewrite. Stress cases cover quoted instructions, contradictory commitments and conditional intent. They are not sealed or statistically independent holdouts and must not be used for tuning. Metadata and tests preserve original requests, synthetic provenance and separation of review voice examples from scenario messages/drafts; this is a leakage guard, not proof of external training-data independence. Existing v1 reports intentionally fail current-dataset validation; regenerate complete report/review/key sets rather than mixing versions.

## Controlled live-test gate

The recorded authorization is one-time: `gpt-5.4-mini`, maximum $2 total, synthetic generate/rewrite integration only. Keep mock defaults. The separate `evaluation.live` runner requires secure credentials, a same-day reviewed official model/pricing/context/output-cap artifact, model-availability preflight, an intact runtime-bound ledger and explicit execution. Reserve both worst-case requests before inference; stop on unknown outcomes, keep reservations, never reset the ledger or renew the allowance.

On October 15, 2026, official [model](https://developers.openai.com/api/docs/models/gpt-5.4-mini.md), [pricing](https://developers.openai.com/api/docs/pricing.md) and [Chat Completions reference](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) were read successfully. They document the approved snapshot `gpt-5.4-mini-2026-03-17`, structured outputs, a 400,000-token context (272,000 maximum input), standard input/output prices of $0.75/$4.50 per million, default-tier standard pricing, and a completion cap that includes visible and reasoning tokens. The global text-only/default-tier runner uses the full context as an input bound and caps output at 512, giving a conservative two-call reservation of **$0.604608**. No caching or batch discount is assumed. Regional endpoints have a documented uplift and are not used by this runner.

Same-day reviewed evidence is retained outside Git at `/workspace/.proofread/reviewed-model-spec-2026-10-15.json`; refresh it from official sources on a later execution date. Both credential names were unset at inspection. Account-specific model availability remains unverified; no paid inference ran and the original ledger remains available with zero reserved calls. A local ledger cannot coordinate multiple machines. If reliable cost bounds or campaign state cannot be established, do not call the API. Use secure environment settings, never chat/Git, for keys.

## Experimental records

Use explicit output paths outside Git for generated reports, review notes and keys; preserve source artifacts and compare the same dataset/seed. Commit only synthetic fixtures and non-sensitive methodology. Record what was actually run, model/configuration, dataset/version/split, metrics, exclusions, cost bounds, outcomes and limitations in implementation status or linked concise experiment records. Keep the answer key separate from reviewers and make no authenticity-superiority claim without meaningful evidence.
