# Route handlers are plain `def`, not `async def`: they call blocking SDKs (Gemini,
# Hugging Face, Supabase, FAISS), and FastAPI runs plain handlers in a thread pool,
# so one slow request no longer stalls every other request on the event loop (R3).
from .chat import router as chat_router
from .generate import router as generate_router
from .image import router as image_router
from .pdf import router as pdf_router

__all__ = ["chat_router", "pdf_router", "image_router", "generate_router"]
