# Proofread

**Say it better. Sound like yourself.**

Proofread is a proposed native iOS communication assistant that helps generate three responses or rewrite a message using recipient, relationship, context and goal, with progressive personalization planned.

## Current status
**Prototype / developer harness, not a production app.** The backend runs by default with fixed example responses; they are **not personalized**. The opt-in OpenAI adapter has offline transport tests, bounded output, and safe error handling; live inference is not yet verified. The SwiftUI application uses a configurable, tested Foundation networking client. Xcode build and simulator tests remain pending.

The PRD, SPEC, AI architecture and roadmap in `docs/` are provisional reconstructions of earlier project discussions, **not the finalized source files**. Reconcile with originals before consequential changes.

## Layout
- `backend/app/main.py`: FastAPI request contracts.
- `backend/app/provider.py`: deterministic mock and opt-in structured-output OpenAI provider.
- `backend/tests/`: API and provider adapter tests.
- `backend/evaluation/`: synthetic-only contract evaluation and blinded human-review templates.
- `ios/`: SwiftUI test harness, configurable networking, Swift Package tests and XcodeGen project spec.
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
To use real inference, securely configure `PROOFREAD_PROVIDER=openai`, `PROOFREAD_MODEL` (compatible with structured JSON schema), and `PROOFREAD_OPENAI_API_KEY` (or legacy `OPENAI_API_KEY`). The `PROOFREAD_` key name supports cloud proxy secret bindings, where `OPENAI_` names are reserved. See `backend/.env.example`. Do **not** commit a secret or send sensitive chat history before privacy review. The adapter has offline transport tests but has not been live-tested; calling the provider may incur charges.

The provider uses OpenAI Chat Completions structured-output JSON schema; [official docs](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create). Unsupported model/version combinations can fail gracefully with an API error.

Provider configuration failures return HTTP 503; upstream failures, refusals and invalid/incomplete output return HTTP 502 with safe messages. Calls have a timeout, a 2048 completion-token cap, and no automatic retries. These bounds do not establish a model budget or production rate limit. Mock rewrites truncate long drafts to fit the candidate contract and cannot establish intent preservation or AI quality. Backend tests block real HTTP transports and isolate provider variables from developer credentials.

The owner authorized a one-time **$2 maximum**, **gpt-5.4-mini** synthetic integration test. That allowance does not enable paid calls automatically. Keep the mock as the default; use the separately gated integration runner only after secure key configuration and verified pricing/capability evidence. See [material requirements and authorization](docs/OPEN_REQUIREMENTS.md).

## Offline evaluation

From `backend`, run `.venv/bin/python -m evaluation run --output /tmp/proofread-eval.json` using a new output filename. The CLI always uses the mock and records contract outcomes, provenance and latency across synthetic generate/rewrite cases. See [evaluation instructions](backend/evaluation/README.md) for reproducible blinded-review templates. Quality remains unmeasured; this does not demonstrate that personalization outperforms generic AI.

## iOS test harness
See [iOS instructions](ios/README.md) for configurable backend endpoints, Foundation networking tests on Linux/macOS, XcodeGen and Simulator setup. Shared Python/Swift fixtures guard wire compatibility. This is a provisional SwiftUI interface, not the approved polished UX; Foundation tests do not verify the SwiftUI application build.

## Guardrails
No real private conversations, API keys, or credentials in the public repository, test data or logs. Consent, deletion and tenant isolation must precede storing conversation imports. Significant changes to UX, costs, architecture and releases require owner approval.

Future Codex tasks discover repository-wide instructions in [AGENTS.md](AGENTS.md). Supporting procedures are in [the engineering protocol](docs/ENGINEERING_PROTOCOL.md); read [implementation status](docs/IMPLEMENTATION_STATUS.md), [decisions](docs/DECISIONS.md) and [next tasks](docs/NEXT_TASKS.md) before development.
