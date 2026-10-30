"""Connection ownership and isolation, using only synthetic MockTransport traffic."""
import asyncio
import json

from fastapi.testclient import TestClient
import httpx
import pytest

import app.main as api
import app.provider as providers
from app.main import ReplyRequest
from app.provider import OpenAIProvider


SAMPLE = {"incoming_message": "synthetic", "relationship": "friend", "goal": "accept"}


def completion():
    return {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"candidates": [
        {"text": "Yes, when?", "label": "Natural"},
        {"text": "I'm in. What time?", "label": "Direct"},
        {"text": "Sounds fun! When?", "label": "Playful"},
    ]})}}]}


@pytest.fixture
def clients(monkeypatch):
    created, requests = [], []
    original = httpx.AsyncClient

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=completion(), headers={"set-cookie": "session=synthetic; Path=/"})

    def factory(*args, **kwargs):
        if kwargs.get("transport") is None:
            kwargs["transport"] = httpx.MockTransport(handler)
        client = original(*args, **kwargs)
        created.append(client)
        return client

    monkeypatch.setattr(providers.httpx, "AsyncClient", factory)
    return created, requests


def test_app_lifespan_reuses_one_client_and_closes_only_on_shutdown(monkeypatch, clients):
    created, requests = clients
    builds = []

    def build():
        builds.append(True)
        return OpenAIProvider("synthetic-key", "synthetic-model")

    monkeypatch.setattr(api, "build_provider", build)
    with TestClient(api.app) as client:
        for _ in range(2):
            assert client.post("/v1/responses", json=SAMPLE).status_code == 200
            assert len(created) == 1
            assert not created[0].is_closed
        assert len(builds) == len(requests) == 2
        assert not created[0].cookies
    assert created[0].is_closed


def test_no_lifespan_fallback_closes_transient_clients(monkeypatch, clients):
    created, _ = clients
    monkeypatch.setattr(api, "build_provider", lambda: OpenAIProvider("synthetic-key", "synthetic-model"))
    client = TestClient(api.app)
    for _ in range(2):
        assert client.post("/v1/responses", json=SAMPLE).status_code == 200
    assert len(created) == 2
    assert all(client.is_closed for client in created)


def test_explicit_transport_is_not_replaced_by_application_pool(monkeypatch, clients):
    created, pooled_requests = clients
    isolated_requests = []

    def handler(request):
        isolated_requests.append(request)
        return httpx.Response(200, json=completion())

    monkeypatch.setattr(api, "build_provider", lambda: OpenAIProvider(
        "synthetic-key", "synthetic-model", transport=httpx.MockTransport(handler)))
    with TestClient(api.app) as client:
        assert client.post("/v1/responses", json=SAMPLE).status_code == 200
        assert len(isolated_requests) == 1
        assert pooled_requests == []
        assert len(created) == 2
        assert not created[0].is_closed and created[1].is_closed
    assert all(client.is_closed for client in created)


def test_mock_mode_never_uses_pooled_network(clients):
    created, requests = clients
    with TestClient(api.app) as client:
        assert client.post("/v1/responses", json=SAMPLE).status_code == 200
        assert requests == []
    assert all(client.is_closed for client in created)


@pytest.mark.asyncio
async def test_borrowed_client_survives_errors_and_cancellation():
    entered = asyncio.Event()
    calls = 0

    async def handler(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429)
        if calls == 2:
            entered.set()
            await asyncio.sleep(10)
        return httpx.Response(200, json=completion())

    async with providers.create_provider_http_client(transport=httpx.MockTransport(handler)) as client:
        provider = OpenAIProvider("synthetic-key", "synthetic-model", client=client)
        request = ReplyRequest(**SAMPLE)
        with pytest.raises(providers.ProviderFailure):
            await provider.generate(request)
        assert not client.is_closed
        task = asyncio.create_task(provider.generate(request))
        await asyncio.wait_for(entered.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert not client.is_closed
        assert len((await provider.generate(request)).candidates) == 3
    assert client.is_closed


@pytest.mark.asyncio
async def test_concurrent_borrowers_keep_credentials_separate_and_reject_cookies():
    requests = []

    async def handler(request):
        requests.append(request)
        await asyncio.sleep(0)
        return httpx.Response(200, json=completion(), headers={"set-cookie": "session=synthetic; Path=/"})

    async with providers.create_provider_http_client(transport=httpx.MockTransport(handler)) as client:
        # Explicit per-request bearer headers must override any default auth.
        client.auth = httpx.BasicAuth("synthetic-user", "synthetic-password")
        first = OpenAIProvider("synthetic-first", "synthetic-model", client=client)
        second = OpenAIProvider("synthetic-second", "synthetic-model", client=client)
        request = ReplyRequest(**SAMPLE)
        await asyncio.gather(first.generate(request), second.generate(request))
        await second.generate(request)
        assert [request.headers["authorization"] for request in requests] == [
            "Bearer synthetic-first", "Bearer synthetic-second", "Bearer synthetic-second"]
        assert all("cookie" not in request.headers for request in requests)
        assert "authorization" not in client.headers
        assert not client.cookies
        assert not client.is_closed


@pytest.mark.asyncio
async def test_client_and_explicit_transport_cannot_be_combined():
    async with providers.create_provider_http_client(transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=completion()))) as client:
        with pytest.raises(ValueError):
            OpenAIProvider("synthetic-key", "synthetic-model", client=client,
                           transport=httpx.MockTransport(lambda _: httpx.Response(200)))
