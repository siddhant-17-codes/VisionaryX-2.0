from fastapi import APIRouter, Depends
from pydantic import BaseModel

from config.logger import setup_logger
from core.rate_limit import gemini_limit
from core.storage import append_turn
from models.schemas import ChatResponse, History, SessionRef, UserText
from routers.deps import owned_session, owner_id
from services.gemini_service import chat

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = setup_logger("visionaryx.chat_router")


class PersistentChatRequest(BaseModel):
    message: UserText
    history: History = []
    chat_session_id: SessionRef | None = None


@router.post("", response_model=ChatResponse, dependencies=[Depends(gemini_limit)])
def send_message(request: PersistentChatRequest, owner: str = Depends(owner_id)):
    session = owned_session(request.chat_session_id, owner)
    generated = chat(request.message, request.history)

    if session:
        append_turn(session, request.message, generated.text, generated.model)
        logger.debug(f"Persisted chat to session: {request.chat_session_id}")

    return ChatResponse(reply=generated.text, model=generated.model)
