import httpx
from google.genai import errors as genai_errors
from google.genai import types

from config.logger import setup_logger
from config.settings import get_settings
from core.exceptions import (
    InvalidImageError,
    LLMError,
    LLMQuotaError,
    LLMUnavailableError,
    UpstreamTimeoutError,
    VisionaryXError,
)
from core.genai_client import get_client
from models.schemas import ChatMessage

settings = get_settings()
logger = setup_logger("visionaryx.gemini")

class _Model:
    """One model in the fallback chain. Tests replace these with fakes."""

    def __init__(self, name: str):
        self.name = name

    def generate_content(self, contents, config: types.GenerateContentConfig | None = None):
        return get_client().models.generate_content(model=self.name, contents=contents, config=config)


_chain = [(name, _Model(name)) for name in settings.gemini_model_list]

# HTTP statuses worth trying the next model for: out of quota, retired, overloaded.
_FALLBACK_CODES = {429, 404, 500, 503, 504}

GEMINI_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/heic", "image/heif"}

RAG_INSTRUCTION ="""You are a precise document assistant. Answer ONLY from the provided context.
If the answer is not in the context, say: "This information is not available in the uploaded documents."
Always be specific and cite relevant details from the context."""


def _should_fall_back(exc: Exception) -> bool:
    if isinstance(exc, genai_errors.APIError):
        return exc.code in _FALLBACK_CODES
    return isinstance(exc, (httpx.TimeoutException, TimeoutError))


def classify_google_error(exc: BaseException) -> VisionaryXError | None:
    """Map a Gemini API failure (possibly wrapped) to a typed error by HTTP status or
    exception type, never by message text. None if it is not one."""
    while exc is not None:
        if isinstance(exc, VisionaryXError):
            return exc
        if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
            return UpstreamTimeoutError()
        if isinstance(exc, genai_errors.APIError):
            if exc.code == 429:
                return LLMQuotaError()
            if exc.code == 504:
                return UpstreamTimeoutError()
            if exc.code in (404, 500, 503):
                return LLMUnavailableError()
            return LLMError(str(exc))
        exc = exc.__cause__
    return None


def _generate(contents, system: str | None = None) -> str:
    config = types.GenerateContentConfig(system_instruction=system) if system else None
    last_error: Exception | None = None
    for name, model in _chain:
        try:
            response = model.generate_content(contents, config=config)
        except Exception as e:
            if not _should_fall_back(e):
                raise
            logger.warning(f"Gemini model {name} failed ({type(e).__name__}): {e}")
            last_error = e
            continue
        if not response.text:
            # Blocked by safety filters or no candidates: retrying another model won't help.
            raise LLMError(f"{name} returned no text")
        return response.text
    raise last_error or LLMUnavailableError()


def _as_llm_error(e: Exception) -> VisionaryXError:
    return classify_google_error(e) or LLMError(str(e))


def _turns(history: list[ChatMessage]) -> list[types.Content]:
    """Conversation history as real multi-turn contents (Gemini calls the assistant 'model')."""
    return [
        types.Content(role="user" if m.role == "user" else "model", parts=[types.Part(text=m.content)])
        for m in history
        if m.content.strip()
    ]


def _user(text: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part(text=text)])


def chat(message: str, history: list[ChatMessage]) -> str:
    try:
        logger.debug(f"Chat request | history_length={len(history)}")
        reply = _generate([*_turns(history), _user(message)])
        logger.debug("Chat response received successfully")
        return reply
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise _as_llm_error(e) from e


def query_with_context(question: str, context: str, history: list[ChatMessage]) -> str:
    try:
        logger.debug(f"RAG query | context_length={len(context)} | history={len(history)}")
        turn = _user(f"Context:\n{context}\n\nQuestion: {question}")
        answer = _generate([*_turns(history), turn], system=RAG_INSTRUCTION)
        logger.debug("RAG query response received")
        return answer
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise _as_llm_error(e) from e


def suggest_questions(document_summary: str) -> list[str]:
    try:
        logger.debug("Generating suggested questions")
        prompt = f"""Based on the following document content, generate exactly 3 insightful questions
a user might want to ask. Return only the questions, one per line, no numbering or bullets.

Document content:
{document_summary[:3000]}

3 questions:"""
        text = _generate(prompt)
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        questions = lines[:3]
        logger.info(f"Generated {len(questions)} suggested questions")
        return questions
    except Exception as e:
        logger.warning(f"Suggest questions failed (non-critical): {e}")
        return []


def analyze_image(image_bytes: bytes, prompt: str) -> str:
    import io

    import PIL.Image
    try:
        image = PIL.Image.open(io.BytesIO(image_bytes))
        image.load()
        mime_type = PIL.Image.MIME.get(image.format or "")
        if mime_type not in GEMINI_IMAGE_TYPES:
            # e.g. GIF (first frame) or BMP: Gemini doesn't accept them, so send a PNG.
            png = io.BytesIO()
            image.convert("RGBA").save(png, format="PNG")
            image_bytes, mime_type = png.getvalue(), "image/png"
    except (OSError, ValueError, PIL.Image.DecompressionBombError) as e:  # OSError covers UnidentifiedImageError
        raise InvalidImageError() from e
    try:
        logger.debug(f"Image analysis | prompt='{prompt[:50]}...'")
        answer = _generate([types.Part.from_bytes(data=image_bytes, mime_type=mime_type), prompt])
        logger.debug("Image analysis complete")
        return answer
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise _as_llm_error(e) from e
