import google.generativeai as genai
from config.settings import get_settings
from config.logger import setup_logger
from core.exceptions import LLMError
from models.schemas import ChatMessage

settings = get_settings()
logger = setup_logger("visionaryx.gemini")
genai.configure(api_key=settings.google_api_key)

_model = genai.GenerativeModel("gemini-2.5-flash")


def chat(message: str, history: list[ChatMessage]) -> str:
    try:
        logger.debug(f"Chat request | history_length={len(history)}")
        history_text = "\n".join(
            [f"{'User' if m.role == 'user' else 'Assistant'}: {m.content}" for m in history]
        )
        full_prompt = f"{history_text}\nUser: {message}\nAssistant:" if history_text else message
        response = _model.generate_content(full_prompt)
        logger.debug("Chat response received successfully")
        return response.text
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise LLMError(str(e))


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
        response = _model.generate_content(prompt)
        logger.debug("RAG query response received")
        return response.text
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise LLMError(str(e))


def suggest_questions(document_summary: str) -> list[str]:
    try:
        logger.debug("Generating suggested questions")
        prompt = f"""Based on the following document content, generate exactly 3 insightful questions
a user might want to ask. Return only the questions, one per line, no numbering or bullets.

Document content:
{document_summary[:3000]}

3 questions:"""
        response = _model.generate_content(prompt)
        lines = [line.strip() for line in response.text.strip().split("\n") if line.strip()]
        questions = lines[:3]
        logger.info(f"Generated {len(questions)} suggested questions")
        return questions
    except Exception as e:
        logger.warning(f"Suggest questions failed (non-critical): {e}")
        return []


def analyze_image(image_bytes: bytes, prompt: str) -> str:
    try:
        import PIL.Image
        import io
        logger.debug(f"Image analysis | prompt='{prompt[:50]}...'")
        image = PIL.Image.open(io.BytesIO(image_bytes))
        response = _model.generate_content([prompt, image])
        logger.debug("Image analysis complete")
        return response.text
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise LLMError(str(e))