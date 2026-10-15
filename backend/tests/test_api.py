from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.provider import OpenAIProvider


client = TestClient(app)
sample = {"incoming_message": "we should hang out", "relationship": "someone I like", "goal": "make plans"}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_generate_three_distinct_candidates():
    response = client.post("/v1/responses", json=sample)
    assert response.status_code == 200
    data = response.json()
    assert len(data["candidates"]) == 3
    assert len({x["text"] for x in data["candidates"]}) == 3
    assert data["personalized"] is False


def test_rewrite_three():
    response = client.post("/v1/responses", json={**sample, "mode": "rewrite", "draft": "see you soon."})
    assert response.status_code == 200
    assert len(response.json()["candidates"]) == 3
    assert "see you soon" in response.json()["candidates"][0]["text"]


def test_requires_draft_when_rewriting():
    assert client.post("/v1/responses", json={**sample, "mode": "rewrite"}).status_code == 422


def test_empty_fields():
    for key in ("incoming_message", "relationship", "goal"):
        assert client.post("/v1/responses", json={**sample, key: " "}).status_code == 422


@pytest.mark.parametrize("draft", [".", "!!!", "?!?", "a" * 10000, "  !  ", "see you soon!", "🙂"])
def test_mock_rewrite_accepts_all_valid_drafts(draft):
    response = client.post("/v1/responses", json={**sample, "mode": "rewrite", "draft": draft})
    assert response.status_code == 200
    candidates = response.json()["candidates"]
    assert len({candidate["text"].strip().casefold() for candidate in candidates}) == 3
    assert all(1 <= len(candidate["text"]) <= 2000 for candidate in candidates)


@pytest.mark.parametrize("provider", ["unknown", "openai"])
def test_provider_configuration_error_is_safe_503(monkeypatch, provider):
    monkeypatch.setenv("PROOFREAD_PROVIDER", provider)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = client.post("/v1/responses", json=sample)
    assert result.status_code == 503
    assert result.json() == {"detail": "AI provider is not configured"}


def test_upstream_failure_is_safe_502(monkeypatch):
    import httpx

    transport = httpx.MockTransport(lambda _: httpx.Response(429, json={"error": "private details"}))
    monkeypatch.setattr("app.main.build_provider", lambda: OpenAIProvider("fake-key", "test-model", transport))
    result = client.post("/v1/responses", json=sample)
    assert result.status_code == 502
    assert result.json() == {"detail": "AI generation is currently unavailable"}
