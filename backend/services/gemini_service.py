import google.generativeai as genai
from google.api_core import exceptions as google_errors

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
from models.schemas import ChatMessage

settings = get_settings()
logger = setup_logger("visionaryx.gemini")
genai.configure(api_key=settings.google_api_key)

# Seconds per model attempt. Three attempts stay inside the frontend's 120s timeout.
LLM_TIMEOUT = 30
# The chain is the retry policy, so the SDK's own retries are switched off.
_REQUEST_OPTIONS = {"timeout": LLM_TIMEOUT, "retry": None}

_chain = [(name, genai.GenerativeModel(name)) for name in settings.gemini_model_list]

# Worth trying the next model: this one is out of quota, overloaded, timed out or retired.
_FALLBACK_ERRORS = (
    google_errors.TooManyRequests,
    google_errors.ServiceUnavailable,
    google_errors.InternalServerError,
    google_errors.DeadlineExceeded,
    google_errors.NotFound,
)


def classify_google_error(exc: BaseException) -> VisionaryXError | None:
    """Map a Google API failure (possibly wrapped, e.g. by LangChain embeddings) to a
    typed error by exception type, never by message text. None if it is not one."""
    while exc is not None:
        if isinstance(exc, VisionaryXError):
            return exc
        if isinstance(exc, google_errors.TooManyRequests):
            return LLMQuotaError()
        if isinstance(exc, (google_errors.DeadlineExceeded, TimeoutError)):
            return UpstreamTimeoutError()
        if isinstance(exc, (google_errors.ServiceUnavailable, google_errors.InternalServerError,
                            google_errors.NotFound)):
            return LLMUnavailableError()
        if isinstance(exc, google_errors.GoogleAPICallError):
            return LLMError(str(exc))
        exc = exc.__cause__
    return None


def _generate(contents) -> str:
    last_error: Exception | None = None
    for name, model in _chain:
        try:
            response = model.generate_content(contents, request_options=_REQUEST_OPTIONS)
            return response.text
        except _FALLBACK_ERRORS as e:
            logger.warning(f"Gemini model {name} failed ({type(e).__name__}): {e}")
            last_error = e
    raise last_error or LLMUnavailableError()


def _as_llm_error(e: Exception) -> VisionaryXError:
    return classify_google_error(e) or LLMError(str(e))


def chat(message: str, history: list[ChatMessage]) -> str:
    try:
        logger.debug(f"Chat request | history_length={len(history)}")
        history_text = "\n".join(
            [f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}" for m in history]
        )
        full_prompt = f"{history_text}\nUser: {message}\nAssistant:" if history_text else message
        reply = _generate(full_prompt)
        logger.debug("Chat response received successfully")
        return reply
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise _as_llm_error(e) from e


def query_with_context(question: str, context: str, history: list[ChatMessage]) -> str:
    try:
        logger.debug(f"RAG query | context_length={len(context)} | history={len(history)}")
        history_text = "\n".join(
            [f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}" for m in history]
        )
        prompt = f"""You are a precise document assistant. Answer ONLY from the provided context.
If the answer is not in the context, say: "This information is not available in the uploaded documents."
Always be specific and cite relevant details from the context.

Context:
{context}

{f'Conversation so far:{chr(10)}{history_text}{chr(10)}' if history_text else ''}
Question: {question}
Answer:"""
        answer = _generate(prompt)
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
    except (OSError, ValueError, PIL.Image.DecompressionBombError) as e:  # OSError covers UnidentifiedImageError
        raise InvalidImageError() from e
    try:
        logger.debug(f"Image analysis | prompt='{prompt[:50]}...'")
        answer = _generate([prompt, image])
        logger.debug("Image analysis complete")
        return answer
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise _as_llm_error(e) from e
