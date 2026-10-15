import httpx
import pytest


def test_real_sync_transport_is_blocked():
    with pytest.raises(AssertionError, match="live HTTP is disabled"):
        httpx.Client(trust_env=False).get("https://example.invalid")


@pytest.mark.asyncio
async def test_real_async_transport_is_blocked():
    async with httpx.AsyncClient(trust_env=False) as client:
        with pytest.raises(AssertionError, match="live HTTP is disabled"):
            await client.get("https://example.invalid")
