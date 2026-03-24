from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from models.schemas import ChatResponse, ChatMessage
from services.gemini_service import chat
from core.storage import append_message
from config.logger import setup_logger

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = setup_logger("visionaryx.chat_router")


class PersistentChatRequest(BaseModel):
    message: str
    history: list = []
    chat_session_id: Optional[str] = None


@router.post("", response_model=ChatResponse)
async def send_message(request: PersistentChatRequest):
    history = [ChatMessage(**m) if isinstance(m, dict) else m for m in request.history]
    reply = chat(request.message, history)

    if request.chat_session_id:
        append_message(request.chat_session_id, "user", request.message)
        append_message(request.chat_session_id, "assistant", reply)
        logger.debug(f"Persisted chat to session: {request.chat_session_id}")

    return ChatResponse(reply=reply)