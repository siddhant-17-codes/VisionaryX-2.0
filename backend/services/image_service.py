"""Text to image with FLUX.1 [schnell]: Cloudflare Workers AI first (free daily
allowance), Hugging Face as the fallback.

When every configured provider says its quota is used up, generation is paused
until the expected reset, so the page can say so honestly and no further calls
are made. The pause lives in memory; a restart simply tries again."""
import base64
import io
import threading
from datetime import UTC, datetime, timedelta

import httpx
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError
from PIL import Image

from config.logger import setup_logger
from config.settings import get_settings
from core.exceptions import ImageGenerationError, ImageQuotaExceededError, UpstreamTimeoutError

settings = get_settings()
logger = setup_logger("visionaryx.image")

PROVIDER_TIMEOUT = 60  # seconds; FLUX schnell normally answers in under 10
CF_MODEL = "@cf/black-forest-labs/flux-1-schnell"
CF_STEPS = 4  # the model's default; each step costs neurons
HF_MODEL = "black-forest-labs/FLUX.1-schnell"
OUTPUT_SIZE = (512, 512)
# Hugging Face credits are monthly and give no reset time; retry after an hour.
HF_RETRY_AFTER = timedelta(hours=1)


class _QuotaUsedUp(Exception):
    """A provider refused because its free quota is used up."""

    def __init__(self, provider: str, resumes_at: datetime):
        super().__init__(f"{provider} quota used up")
        self.provider = provider
        self.resumes_at = resumes_at


_paused_until: datetime | None = None
_pause_lock = threading.Lock()


def _now() -> datetime:
    return datetime.now(UTC)


def _next_utc_midnight() -> datetime:
    """Cloudflare resets the Workers AI free allowance daily at 00:00 UTC."""
    tomorrow = _now().date() + timedelta(days=1)
    return datetime(tomorrow.year, tomorrow.month, tomorrow.day, tzinfo=UTC)


def _cloudflare(prompt: str) -> Image.Image:
    url = (f"https://api.cloudflare.com/client/v4/accounts/{settings.cloudflare_account_id}"
           f"/ai/run/{CF_MODEL}")
    res = httpx.post(url, headers={"Authorization": f"Bearer {settings.cloudflare_api_token}"},
                     json={"prompt": prompt, "steps": CF_STEPS}, timeout=PROVIDER_TIMEOUT)
    body = res.json() if res.headers.get("content-type", "").startswith("application/json") else {}
    codes = {e.get("code") for e in body.get("errors") or [] if isinstance(e, dict)}
    # The docs don't say how an exhausted daily allowance is reported; 429 is the
    # standard status, and 4006 is the error code reported for it outside the docs.
    if res.status_code == 429 or 4006 in codes:
        raise _QuotaUsedUp("cloudflare", _next_utc_midnight())
    res.raise_for_status()
    image_b64 = (body.get("result") or {}).get("image")
    if not image_b64:
        raise ImageGenerationError(f"Cloudflare returned no image (status {res.status_code})")
    return Image.open(io.BytesIO(base64.b64decode(image_b64)))


def _huggingface(prompt: str) -> Image.Image:
    client = InferenceClient(provider="auto", token=settings.huggingfacehub_api_token, timeout=PROVIDER_TIMEOUT)
    try:
        return client.text_to_image(prompt, model=HF_MODEL)
    except HfHubHTTPError as e:
        if getattr(e.response, "status_code", None) == 402:
            raise _QuotaUsedUp("huggingface", _now() + HF_RETRY_AFTER) from e
        raise


def _providers():
    if settings.cloudflare_account_id and settings.cloudflare_api_token:
        yield "cloudflare", _cloudflare
    yield "huggingface", _huggingface


def pause_status() -> datetime | None:
    """When generation is expected back, or None if it is available now."""
    with _pause_lock:
        if _paused_until and _now() < _paused_until:
            return _paused_until
    return None


def _retry_after(until: datetime) -> int:
    return max(1, int((until - _now()).total_seconds()))


def generate_image(prompt: str) -> str:
    global _paused_until
    paused = pause_status()
    if paused:
        raise ImageQuotaExceededError(_retry_after(paused))

    logger.info(f"Image generation | prompt='{prompt[:60]}...'")
    failures: list[Exception] = []
    for name, provider in _providers():
        try:
            image = provider(prompt)
            break
        except Exception as e:
            logger.warning(f"Image provider {name} failed ({type(e).__name__}): {e}")
            failures.append(e)
    else:
        if all(isinstance(e, _QuotaUsedUp) for e in failures):
            # Cloudflare's reset time is documented (00:00 UTC); Hugging Face's is a guess.
            known = [e.resumes_at for e in failures if e.provider == "cloudflare"]
            resumes_at = known[0] if known else min(e.resumes_at for e in failures)
            with _pause_lock:
                _paused_until = resumes_at
            logger.error(f"Image generation paused until {resumes_at.isoformat()}")
            raise ImageQuotaExceededError(_retry_after(resumes_at)) from failures[-1]
        if any(isinstance(e, httpx.TimeoutException) for e in failures):
            raise UpstreamTimeoutError() from failures[-1]
        raise ImageGenerationError("; ".join(f"{type(e).__name__}: {e}" for e in failures)) from failures[-1]

    buffer = io.BytesIO()
    image.convert("RGB").resize(OUTPUT_SIZE).save(buffer, format="PNG")
    logger.info(f"Image generation successful via {name}")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
