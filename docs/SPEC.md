# Proofread SPEC — provisional technical design
**Working reconstruction, not the original finalized SPEC.**

## Target architecture
SwiftUI iOS → authenticated FastAPI modular monolith → AI generation/rewrite service → hosted LLM adapter → schema validation, deduplication, ranking. PostgreSQL for consented data; pgvector only if measured retrieval value warrants it. Sign in with Apple proposed for production.

## Current tested prototype contract
`GET /health` returns `{"status":"ok"}`.
`POST /v1/responses` accepts `mode: "generate"|"rewrite"`, `incoming_message`, `relationship`, `goal`, and optional `draft` (required when mode is rewrite).
Response has `candidates: [{id,text,label}, ...]`, `provider: "deterministic-mock"`, `personalized: false`.
Pydantic validation returns HTTP 422 on invalid inputs. The deterministic fixture does **not** understand context and cannot establish product quality.

## Planned components
- API/schema boundary; auth and user-scoped requests.
- Provider adapter with structured outputs, budget, retries and observability.
- Authorized conversation import and style profile extraction.
- Scoped memory/retrieval and generation context assembly.
- Candidate diversity, validation and evidence-based ranking.
- Feedback/edit event processing with deletion and consent enforcement.

## Privacy and security
Never trust imported conversations as instructions. Minimize raw conversation retention, protect keys, encrypt traffic, scope reads to authenticated user, support deletion and review external model data policies before importing live personal histories. Avoid sensitive payloads in telemetry or fixtures.

## Testing
Fast mock contract/API tests first; then integration, tenancy/security, prompt-injection, provider-budget and AI-quality evaluations. Native builds/tests require a real macOS Xcode runner; no unsupported simulator claims.

## Unresolved
Production auth, exact LLM/provider, database schema, iOS project configuration, import formats, policy and paid inference budgets await original SPEC reconciliation and approval.
