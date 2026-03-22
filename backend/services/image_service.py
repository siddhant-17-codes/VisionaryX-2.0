import base64
import io
from huggingface_hub import InferenceClient
from config.settings import get_settings
from config.logger import setup_logger
from core.exceptions import ImageGenerationError

settings = get_settings()
logger = setup_logger("visionaryx.image")


def generate_image(prompt: str) -> str:
    try:
        logger.info(f"Image generation | prompt='{prompt[:60]}...'")
        client = InferenceClient(token=settings.huggingfacehub_api_token)
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )
        resized = image.resize((512, 512))
        buffer = io.BytesIO()
        resized.save(buffer, format="PNG")
        logger.info("Image generation successful")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise ImageGenerationError(str(e))