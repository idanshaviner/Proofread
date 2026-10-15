"""Tests are independent of developer credentials and never call a live provider."""
import httpx
import pytest


@pytest.fixture(autouse=True)
def offline_provider_environment(monkeypatch):
    monkeypatch.setenv("PROOFREAD_PROVIDER", "mock")
    monkeypatch.delenv("PROOFREAD_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def deny_network(*args, **kwargs):
        raise AssertionError("Use httpx.MockTransport; live HTTP is disabled in tests")

    async def deny_async_network(*args, **kwargs):
        deny_network()

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", deny_network)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", deny_async_network)
