# Proofread

**Say it better. Sound like yourself.**

Proofread is a proposed native iOS AI communication assistant that generates three replies or rewrites a draft based on recipient, relationship, conversation context, user goal, and—eventually—an authorized personal writing-style profile.

## Current state
Early **deterministic mock API**, not a working personalized AI or production app. SwiftUI source is available in the previous downloadable starter archive but has not yet been committed or built in Xcode. The original finalized PRD, SPEC, AI research and roadmap from the ChatGPT Project are not present here; docs/ versions are explicitly **provisional reconstructions** awaiting reconciliation.

## Repository
- `backend/app/main.py` — FastAPI endpoints and fixed mock output.
- `backend/tests/test_api.py` — API contract tests.
- `docs/PRD.md` — product requirements draft.
- `docs/SPEC.md` — technical contract draft.
- `docs/AI_ARCHITECTURE.md` — personalization hypothesis.
- `docs/ROADMAP.md` — staged plan.
- `docs/IMPLEMENTATION_STATUS.md` — verified progress.
- `docs/DECISIONS.md` and `AGENTS.md` — durable engineering context.

## Run
Python 3.11+:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Docs: http://127.0.0.1:8000/docs

## Test
```bash
cd backend && python -m pytest -q
```

## Example request
```bash
curl -X POST http://127.0.0.1:8000/v1/responses -H 'Content-Type: application/json' -d '{"mode":"generate","incoming_message":"haha we should hang out sometime","relationship":"someone I like","goal":"make casual plans"}'
```

The mock returns exactly three fixed example suggestions, `provider: deterministic-mock`, and `personalized: false`. It does NOT currently tailor replies to message/context/goal.

**Privacy:** Do not put real private message history, tokens, or keys in a public repo, tests or logs. No real conversation ingestion until consent, retention and deletion flows are approved.

## Roadmap
Validate both generate and rewrite end-to-end; add native SwiftUI/Xcode integration and a hosted model provider; then secure persistence, imported history, personalized style extraction/retrieval, feedback, evaluation and private beta. See docs/ROADMAP.md and docs/IMPLEMENTATION_STATUS.md.

Substantive changes should use reviewed branches. Owner approval is required for major UX, privacy, architecture, cost and release decisions.
