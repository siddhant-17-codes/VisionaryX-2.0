import json
import os
import shutil
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional
from config.logger import setup_logger

logger = setup_logger("visionaryx.storage")

CHATS_DIR = "storage/chats"
DOCS_DIR = "storage/documents"


@dataclass
class ChatSession:
    id: str
    title: str
    mode: str  # "chat" | "pdf"
    created_at: str
    updated_at: str
    messages: list
    session_id: Optional[str] = None  # PDF session_id if mode == "pdf"
    documents: Optional[list] = None  # filenames if mode == "pdf"


def _ensure_dirs():
    os.makedirs(CHATS_DIR, exist_ok=True)
    os.makedirs(DOCS_DIR, exist_ok=True)


def create_chat_session(mode: str = "chat", title: str = "New chat") -> ChatSession:
    _ensure_dirs()
    session = ChatSession(
        id=str(uuid.uuid4()),
        title=title,
        mode=mode,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        messages=[],
        session_id=None,
        documents=[],
    )
    _save_session(session)
    logger.info(f"Created chat session: {session.id} | mode={mode}")
    return session


def _save_session(session: ChatSession):
    _ensure_dirs()
    path = os.path.join(CHATS_DIR, f"{session.id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(session), f, ensure_ascii=False, indent=2)


def load_session(session_id: str) -> Optional[ChatSession]:
    path = os.path.join(CHATS_DIR, f"{session_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return ChatSession(**data)


def list_sessions() -> list[dict]:
    _ensure_dirs()
    sessions = []
    for fname in os.listdir(CHATS_DIR):
        if fname.endswith(".json"):
            path = os.path.join(CHATS_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                sessions.append({
                    "id": data["id"],
                    "title": data["title"],
                    "mode": data["mode"],
                    "created_at": data["created_at"],
                    "updated_at": data["updated_at"],
                    "message_count": len(data.get("messages", [])),
                    "documents": data.get("documents", []),
                })
            except Exception as e:
                logger.warning(f"Could not read session {fname}: {e}")
    return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)


def append_message(session_id: str, role: str, content: str) -> Optional[ChatSession]:
    session = load_session(session_id)
    if not session:
        return None
    session.messages.append({"role": role, "content": content})
    session.updated_at = datetime.now().isoformat()
    if len(session.messages) == 2 and session.title == "New chat":
        first_user_msg = next((m["content"] for m in session.messages if m["role"] == "user"), "")
        session.title = first_user_msg[:50] + ("..." if len(first_user_msg) > 50 else "")
    _save_session(session)
    return session


def update_session_pdf(session_id: str, pdf_session_id: str, filenames: list[str]):
    session = load_session(session_id)
    if not session:
        return
    session.session_id = pdf_session_id
    session.documents = filenames
    session.updated_at = datetime.now().isoformat()
    if session.title == "New chat" and filenames:
        session.title = filenames[0]
    _save_session(session)
    logger.info(f"Updated session {session_id} with PDF data: {filenames}")


def delete_session(session_id: str) -> bool:
    path = os.path.join(CHATS_DIR, f"{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
        doc_path = os.path.join(DOCS_DIR, session_id)
        if os.path.exists(doc_path):
            shutil.rmtree(doc_path)
        logger.info(f"Deleted session: {session_id}")
        return True
    return False


def save_document(chat_session_id: str, filename: str, file_bytes: bytes):
    doc_dir = os.path.join(DOCS_DIR, chat_session_id)
    os.makedirs(doc_dir, exist_ok=True)
    path = os.path.join(doc_dir, filename)
    with open(path, "wb") as f:
        f.write(file_bytes)
    logger.info(f"Saved document: {filename} → {path}")