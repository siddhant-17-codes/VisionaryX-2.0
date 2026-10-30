import base64
import io

import httpx
from huggingface_hub.errors import HfHubHTTPError
from PIL import Image

from tests.conftest import fixture_bytes


def test_image_query_sends_prompt_and_image(client, gemini):
    res = client.post(
        "/api/image/query",
        files={"file": ("bars.png", fixture_bytes("bars.png"), "image/png")},
        data={"prompt": "How many bars?"},
    )
    assert res.status_code == 200
    assert res.json()["answer"] == gemini.answer
    prompt, image = gemini.prompts[-1]
    assert prompt == "How many bars?"
    assert image.size == (640, 400)


def test_image_query_rejects_non_image(client):
    res = client.post("/api/image/query", files={"file": ("x.png", b"not an image", "image/png")})
    assert res.status_code == 400


def test_generate_returns_png(client):
    res = client.post("/api/generate/image", json={"prompt": "a red apple"})
    assert res.status_code == 200
    img = Image.open(io.BytesIO(base64.b64decode(res.json()["image_base64"])))
    assert img.format == "PNG"


def _hf_error(status: int) -> HfHubHTTPError:
    response = httpx.Response(status, request=httpx.Request("POST", "https://router.huggingface.co/x"))
    return HfHubHTTPError(f"HTTP {status}", response=response)


def test_generate_out_of_credits_returns_503(client, hf):
    hf.error = _hf_error(402)
    res = client.post("/api/generate/image", json={"prompt": "a red apple"})
    assert res.status_code == 503
    assert res.json()["type"] == "ImageQuotaExceededError"


def test_generate_other_failure_returns_502(client, hf):
    hf.error = _hf_error(500)
    res = client.post("/api/generate/image", json={"prompt": "a red apple"})
    assert res.status_code == 502
