from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, StringConstraints

from config.logger import setup_logger
from core.rate_limit import sessions_limit
from core.storage import (
    create_chat_session,
    delete_session,
    list_sessions,
    load_session,
)
from routers.deps import owner_id

router = APIRouter(prefix="/api/sessions", tags=["sessions"], dependencies=[Depends(sessions_limit)])
logger = setup_logger("visionaryx.sessions")


class CreateSessionRequest(BaseModel):
    mode: Literal["chat", "pdf", "image", "generate"] = "chat"
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)] = "New chat"


class SessionResponse(BaseModel):
    id: str
    title: str
    mode: str
    created_at: str
    updated_at: str
    messages: list[dict]
    session_id: str | None = None
    documents: list[str] | None = None


@router.post("", response_model=SessionResponse)
def create_session(request: CreateSessionRequest, owner: str = Depends(owner_id)):
    session = create_chat_session(owner, mode=request.mode, title=request.title)
    return SessionResponse(**session.__dict__)


@router.get("", response_model=list[dict])
def get_sessions(owner: str = Depends(owner_id)):
    return list_sessions(owner)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, owner: str = Depends(owner_id)):
    session = load_session(session_id, owner)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return SessionResponse(**session.__dict__)


@router.delete("/{session_id}")
def remove_session(session_id: str, owner: str = Depends(owner_id)):
    deleted = delete_session(session_id, owner)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return {"deleted": True, "session_id": session_id}
