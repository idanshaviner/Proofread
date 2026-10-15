from fastapi.testclient import TestClient
from app.main import app

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
