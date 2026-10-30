import base64
import io

from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError

from config.logger import setup_logger
from config.settings import get_settings
from core.exceptions import ImageGenerationError, ImageQuotaExceededError

settings = get_settings()
logger = setup_logger("visionaryx.image")


def generate_image(prompt: str) -> str:
    try:
        logger.info(f"Image generation | prompt='{prompt[:60]}...'")
        client = InferenceClient(
            provider="auto",
            token=settings.huggingfacehub_api_token,
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
    except HfHubHTTPError as e:
        logger.error(f"Image generation failed: {e}")
        if getattr(e.response, "status_code", None) == 402:
            raise ImageQuotaExceededError() from e
        raise ImageGenerationError(str(e)) from e
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise ImageGenerationError(str(e)) from e