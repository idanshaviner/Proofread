import json
import httpx
import pytest
from fastapi.testclient import TestClient
from app.main import app, ReplyRequest
from app.provider import OpenAIProvider, ProviderFailure, build_provider

@pytest.mark.asyncio
async def test_structured_model_output():
    def handler(request: httpx.Request):
        body = json.loads(request.content)
        assert request.headers["Authorization"] == "Bearer fake-key"
        assert body["response_format"]["type"] == "json_schema"
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"candidates": [
            {"text": "sounds good", "label": "Natural"},
            {"text": "let's do it", "label": "Direct"},
            {"text": "about time lol", "label": "Playful"}]})}}]})
    model = OpenAIProvider("fake-key", "test-model", httpx.MockTransport(handler))
    answer = await model.generate(ReplyRequest(incoming_message="hey", relationship="friend", goal="agree"))
    assert len(answer.candidates) == 3 and answer.personalized is False

@pytest.mark.asyncio
async def test_duplicate_model_output_rejected():
    def handler(_):
        return httpx.Response(200, json={"choices": [{"message": {"content": json.dumps({"candidates": [
            {"text": "same", "label": "Natural"}, {"text": "same", "label": "Direct"}, {"text": "other", "label": "Playful"}]})}}]})
    model = OpenAIProvider("fake-key", "test-model", httpx.MockTransport(handler))
    with pytest.raises(ProviderFailure):
        await model.generate(ReplyRequest(incoming_message="hey", relationship="friend", goal="agree"))

def test_credentials_required(monkeypatch):
    monkeypatch.setenv("PROOFREAD_PROVIDER", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        build_provider()

def test_mock_default(monkeypatch):
    monkeypatch.delenv("PROOFREAD_PROVIDER", raising=False)
    result = TestClient(app).post("/v1/responses", json={"incoming_message": "hey", "relationship": "friend", "goal": "reply"})
    assert result.status_code == 200 and result.json()["provider"] == "deterministic-mock"
