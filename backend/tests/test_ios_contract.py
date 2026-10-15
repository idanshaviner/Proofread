"""Keep the Swift client's synthetic wire fixtures aligned with the real API."""
import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.provider import OpenAIProvider


FIXTURES = Path(__file__).resolve().parents[2] / "ios/Tests/ProofreadNetworkingTests/Fixtures"
SAMPLE = {"incoming_message": "Want to meet?", "relationship": "friend", "goal": "make plans"}


@pytest.mark.parametrize("mode", ["generate", "rewrite"])
def test_ios_success_fixtures_match_backend(mode, monkeypatch):
    monkeypatch.setenv("PROOFREAD_PROVIDER", "mock")
    payload = {**SAMPLE, "mode": mode}
    if mode == "rewrite":
        payload["draft"] = "See you soon."
    response = TestClient(app).post("/v1/responses", json=payload)
    assert response.status_code == 200
    assert response.json() == json.loads((FIXTURES / f"{mode}.json").read_text())


def test_ios_validation_fixture_matches_backend():
    response = TestClient(app).post("/v1/responses", json={**SAMPLE, "mode": "rewrite"})
    assert response.status_code == 422
    assert response.json() == json.loads((FIXTURES / "validation-error.json").read_text())


def test_ios_provider_error_fixture_matches_backend(monkeypatch):
    transport = httpx.MockTransport(lambda _: httpx.Response(429, json={"error": "synthetic private detail"}))
    monkeypatch.setattr("app.main.build_provider", lambda: OpenAIProvider("fake-key", "test-model", transport))
    response = TestClient(app).post("/v1/responses", json=SAMPLE)
    assert response.status_code == 502
    assert response.json() == json.loads((FIXTURES / "provider-error.json").read_text())
