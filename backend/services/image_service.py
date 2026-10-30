import base64
import io

import httpx
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from config.logger import setup_logger
from config.settings import get_settings
from core.exceptions import ImageGenerationError, ImageQuotaExceededError, UpstreamTimeoutError

settings = get_settings()
logger = setup_logger("visionaryx.image")

HF_TIMEOUT = 60  # seconds; FLUX schnell normally answers in under 10


def generate_image(prompt: str) -> str:
    try:
        logger.info(f"Image generation | prompt='{prompt[:60]}...'")
        client = InferenceClient(
            provider="auto",
            token=settings.huggingfacehub_api_token,
            timeout=HF_TIMEOUT,
        )
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )
        resized = image.resize((512, 512))
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        logger.info("Image generation successful")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except httpx.TimeoutException as e:
        logger.error(f"Image generation timed out: {e}")
        raise UpstreamTimeoutError() from e
    except HfHubHTTPError as e:
        logger.error(f"Image generation failed: {e}")
        if getattr(e.response, "status_code", None) == 402:
            raise ImageQuotaExceededError() from e
        raise ImageGenerationError(str(e)) from e
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise ImageGenerationError(str(e)) from e