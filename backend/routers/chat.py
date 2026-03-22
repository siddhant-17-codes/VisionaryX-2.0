from fastapi import APIRouter
from models.schemas import ChatRequest, ChatResponse
from services.gemini_service import chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    reply = chat(request.message, request.history)
    return ChatResponse(reply=reply)
