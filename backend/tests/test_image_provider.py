"""Image provider chain: Cloudflare Workers AI first, Hugging Face as fallback, and an
honest paused state when every free quota is used up."""
import base64
import io
from datetime import UTC, datetime

import httpx
import pytest
from huggingface_hub.errors import HfHubHTTPError
from PIL import Image

import services.image_service as image_service

PROMPT = {"prompt": "a red apple"}


def jpeg_b64(size=(1024, 1024)) -> str:
    out = io.BytesIO()
    Image.new("RGB", size, "green").save(out, format="JPEG")
    return base64.b64encode(out.getvalue()).decode()


class FakeCloudflare:
    def __init__(self):
        self.status, self.error, self.calls = 200, None, []
        self.body = {"result": {"image": jpeg_b64()}, "success": True}

    def post(self, url, headers, json, timeout):
        self.calls.append((url, headers, json))
        if self.error:
            raise self.error
        return httpx.Response(self.status, json=self.body, request=httpx.Request("POST", url))


@pytest.fixture
def cloudflare(monkeypatch):
    fake = FakeCloudflare()
    monkeypatch.setattr(image_service.settings, "cloudflare_account_id", "acct123")
    monkeypatch.setattr(image_service.settings, "cloudflare_api_token", "cf-token")
    monkeypatch.setattr(image_service.httpx, "post", fake.post)
    return fake


def hf_error(status: int) -> HfHubHTTPError:
    response = httpx.Response(status, request=httpx.Request("POST", "https://router.huggingface.co/x"))
    return HfHubHTTPError(f"HTTP {status}", response=response)


def decoded(res) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(res.json()["image_base64"])))


def test_cloudflare_is_tried_first_with_the_documented_request(client, cloudflare, hf):
    hf.error = AssertionError("Hugging Face must not be called")
    res = client.post("/api/generate/image", json=PROMPT)
    assert res.status_code == 200
    img = decoded(res)
    assert img.format == "PNG" and img.size == (512, 512)
    url, headers, body = cloudflare.calls[0]
    assert url == ("https://api.cloudflare.com/client/v4/accounts/acct123"
                   "/ai/run/@cf/black-forest-labs/flux-1-schnell")
    assert headers == {"Authorization": "Bearer cf-token"}
    assert body == {"prompt": "a red apple", "steps": 4}


@pytest.mark.parametrize("failure", ["server_error", "timeout", "no_image"])
def test_cloudflare_failure_falls_back_to_hugging_face(client, cloudflare, hf, failure):
    if failure == "server_error":
        cloudflare.status, cloudflare.body = 500, {"success": False, "errors": [{"code": 1000}]}
    elif failure == "timeout":
        cloudflare.error = httpx.ReadTimeout("slow")
    else:
        cloudflare.body = {"result": {}, "success": True}
    res = client.post("/api/generate/image", json=PROMPT)
    assert res.status_code == 200
    assert decoded(res).size == (512, 512)


def test_without_cloudflare_settings_only_hugging_face_is_used(client, hf, monkeypatch):
    monkeypatch.setattr(image_service.httpx, "post", lambda *a, **k: pytest.fail("Cloudflare called"))
    assert client.post("/api/generate/image", json=PROMPT).status_code == 200


@pytest.mark.parametrize("cf_quota", [
    {"status": 429, "body": {"success": False, "errors": [{"code": 4006}]}},
    {"status": 400, "body": {"success": False, "errors": [{"code": 4006}]}},
])
def test_every_quota_used_up_pauses_until_cloudflare_resets(client, cloudflare, hf, cf_quota):
    cloudflare.status, cloudflare.body = cf_quota["status"], cf_quota["body"]
    hf.error = hf_error(402)

    res = client.post("/api/generate/image", json=PROMPT)
    assert res.status_code == 503
    assert res.json()["type"] == "ImageQuotaExceededError"
    midnight = image_service._next_utc_midnight()
    assert abs(int(res.headers["Retry-After"]) - (midnight - datetime.now(UTC)).total_seconds()) < 5

    status = client.get("/api/generate/status").json()
    assert status == {"available": False, "resumes_at": midnight.isoformat()}

    # While paused, no provider is called at all.
    calls = len(cloudflare.calls)
    assert client.post("/api/generate/image", json=PROMPT).status_code == 503
    assert len(cloudflare.calls) == calls


def test_one_quota_plus_a_real_failure_is_not_reported_as_paused(client, cloudflare, hf):
    cloudflare.status, cloudflare.body = 429, {"success": False, "errors": []}
    hf.error = hf_error(500)
    res = client.post("/api/generate/image", json=PROMPT)
    assert res.status_code == 502
    assert client.get("/api/generate/status").json() == {"available": True, "resumes_at": None}


def test_hugging_face_only_pause_retries_after_an_hour(client, hf):
    hf.error = hf_error(402)
    res = client.post("/api/generate/image", json=PROMPT)
    assert res.status_code == 503
    assert 3590 <= int(res.headers["Retry-After"]) <= 3600


def test_status_is_available_by_default(client):
    assert client.get("/api/generate/status").json() == {"available": True, "resumes_at": None}


def test_one_visitor_gets_at_most_20_images_a_day(client, hf):
    from core.rate_limit import generate_daily_limit, generate_limit
    ip = {"CF-Connecting-IP": "203.0.113.9"}
    for _ in range(20):
        generate_limit.reset()  # isolate the daily limit from the per-minute one
        assert client.post("/api/generate/image", json=PROMPT, headers=ip).status_code == 200
    generate_limit.reset()
    res = client.post("/api/generate/image", json=PROMPT, headers=ip)
    assert res.status_code == 429
    assert generate_daily_limit.limit == 20
