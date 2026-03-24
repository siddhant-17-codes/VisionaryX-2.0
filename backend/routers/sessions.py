from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core.storage import (
    create_chat_session,
    load_session,
    list_sessions,
    delete_session,
)
from config.logger import setup_logger

router = APIRouter(prefix="/api/sessions", tags=["sessions"])
logger = setup_logger("visionaryx.sessions")


class CreateSessionRequest(BaseModel):
    mode: str = "chat"
    title: str = "New chat"


class SessionResponse(BaseModel):
    id: str
    title: str
    mode: str
    created_at: str
    updated_at: str
    messages: list
    session_id: Optional[str] = None
    documents: Optional[list] = None


@router.post("", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    session = create_chat_session(mode=request.mode, title=request.title)
    return SessionResponse(**session.__dict__)


@router.get("", response_model=list[dict])
async def get_sessions():
    return list_sessions()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    session = load_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return SessionResponse(**session.__dict__)


@router.delete("/{session_id}")
async def remove_session(session_id: str):
    deleted = delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return {"deleted": True, "session_id": session_id}