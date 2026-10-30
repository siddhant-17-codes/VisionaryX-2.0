"""R3: a slow model call must not stall unrelated requests. TestClient runs each
request on its own event loop, so this uses one shared loop via ASGITransport."""
import asyncio
import time

import httpx
import pytest

from tests.conftest import OWNER

SLOW = 1.0


@pytest.mark.anyio
async def test_slow_chat_does_not_block_other_requests(supabase, gemini, hf, monkeypatch):
    from main import app

    real = gemini.generate_content

    def slow_generate(*args, **kwargs):
        time.sleep(SLOW)  # a blocking SDK call, like the real Gemini client
        return real(*args, **kwargs)
    monkeypatch.setattr(gemini, "generate_content", slow_generate)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", headers={"X-Client-Id": OWNER}) as ac:
        start = time.perf_counter()

        async def chat():
            return await ac.post("/api/chat", json={"message": "hi"})

        async def health_while_chat_runs():
            await asyncio.sleep(0.1)
            res = await ac.get("/health")
            return res, time.perf_counter() - start

        chat_res, (health_res, health_done) = await asyncio.gather(chat(), health_while_chat_runs())

    assert chat_res.status_code == 200 and health_res.status_code == 200
    assert health_done < SLOW / 2, f"/health waited {health_done:.2f}s for the slow chat"


@pytest.fixture
def anyio_backend():
    return "asyncio"
