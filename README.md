# Proofread

**Say it better. Sound like yourself.**

Proofread is a proposed native iOS communication assistant that helps generate three responses or rewrite a message using recipient, relationship, context and goal, with progressive personalization planned.

## Current status
**Prototype / developer harness, not a production app.** The backend runs by default with fixed example responses; they are **not personalized**. Real-model generation is available as an opt-in adapter, but live inference is not yet verified. Native SwiftUI source and an XcodeGen project spec are committed, but Xcode build and simulator tests are pending.

The PRD, SPEC, AI architecture and roadmap in `docs/` are provisional reconstructions of earlier project discussions, **not the finalized source files**. Reconcile with originals before consequential changes.

## Layout
- `backend/app/main.py`: FastAPI request contracts.
- `backend/app/provider.py`: deterministic mock and opt-in structured-output OpenAI provider.
- `backend/tests/`: API and provider adapter tests.
- `ios/`: SwiftUI test-harness screens, models, networking and XcodeGen project spec.
- `docs/`: PRD, SPEC, architecture, roadmap, decisions, implementation status.
- `AGENTS.md`: development instructions.

## Backend
Requires Python 3.11+:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. The API exposes `GET /health` and `POST /v1/responses`. Request body: `{"mode":"generate","incoming_message":"hey","relationship":"friend","goal":"reply"}`; mode `rewrite` additionally requires nonblank `draft`. Response includes three candidates, provider name and `personalized:false`.

## Opt-in AI provider
Default environment: `PROOFREAD_PROVIDER=mock` (no credentials, no charges).
To use real inference, securely configure `PROOFREAD_PROVIDER=openai`, `PROOFREAD_MODEL` (compatible with structured JSON schema), and `OPENAI_API_KEY`. See `backend/.env.example`. Do **not** commit a secret or send sensitive chat history before privacy review. The adapter is code-complete for mock tests but has not been live-tested; calling the provider may incur charges.

The provider uses OpenAI Chat Completions structured-output JSON schema; [official docs](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create). Unsupported model/version combinations can fail gracefully with an API error.

## iOS test harness
See `ios/README.md` for XcodeGen and Simulator setup. This is a provisional SwiftUI interface, not the approved polished UX, and cannot yet be considered build-verified.

## Guardrails
No real private conversations, API keys, or credentials in the public repository, test data or logs. Consent, deletion and tenant isolation must precede storing conversation imports. Significant changes to UX, costs, architecture and releases require owner approval.

See `docs/IMPLEMENTATION_STATUS.md` for verified status and the next tasks.
