from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from config.logger import setup_logger
from core.storage import append_turn, load_session
from models.schemas import ChatMessage, ChatResponse
from routers.deps import owner_id
from services.gemini_service import chat

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = setup_logger("visionaryx.chat_router")


class PersistentChatRequest(BaseModel):
    message: str
    history: list = []
    chat_session_id: str | None = None


@router.post("", response_model=ChatResponse)
async def send_message(request: PersistentChatRequest, owner: str = Depends(owner_id)):
    # Check ownership before calling the model so a bad session id costs no quota.
    if request.chat_session_id and not load_session(request.chat_session_id, owner):
        raise HTTPException(status_code=404, detail=f"Session '{request.chat_session_id}' not found.")

    history = [ChatMessage(**m) if isinstance(m, dict) else m for m in request.history]
    reply = chat(request.message, history)

    if request.chat_session_id:
        append_turn(request.chat_session_id, owner, request.message, reply)
        logger.debug(f"Persisted chat to session: {request.chat_session_id}")

    return ChatResponse(reply=reply)
