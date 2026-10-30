import base64
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime

from supabase import Client, create_client

from config.logger import setup_logger

logger = setup_logger("visionaryx.storage")

def _get_client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

TABLE = "sessions"

@dataclass
class ChatSession:
    id: str
    title: str
    mode: str
    created_at: str
    updated_at: str
    messages: list
    session_id: str | None = None
    documents: list | None = None
    owner_id: str | None = None


# Every read and write below is scoped to owner_id (the browser's X-Client-Id).
# A row owned by someone else behaves exactly like a missing row.

def create_chat_session(owner_id: str, mode: str = "chat", title: str = "New chat") -> ChatSession:
    session = ChatSession(
        id=str(uuid.uuid4()), title=title, mode=mode,
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        messages=[], session_id=None, documents=[], owner_id=owner_id,
    )
    _get_client().table(TABLE).insert(asdict(session)).execute()
    logger.info(f"Created session: {session.id} | mode={mode}")
    return session


def load_session(session_id: str, owner_id: str) -> ChatSession | None:
    res = _get_client().table(TABLE).select("*").eq("id", session_id).eq("owner_id", owner_id).execute()
    if not res.data:
        return None
    return ChatSession(**res.data[0])


def list_sessions(owner_id: str) -> list[dict]:
    res = _get_client().table(TABLE).select(
        "id,title,mode,created_at,updated_at,documents,messages"
    ).eq("owner_id", owner_id).order("updated_at", desc=True).execute()
    return [{
        "id": r["id"], "title": r["title"], "mode": r["mode"],
        "created_at": r["created_at"], "updated_at": r["updated_at"],
        "message_count": len(r.get("messages") or []), "documents": r.get("documents") or [],
    } for r in res.data]


def append_turn(session_id: str, owner_id: str, question: str, answer: str) -> ChatSession | None:
    session = load_session(session_id, owner_id)
    if not session:
        return None
    session.messages.append({"role": "user", "content": question})
    session.messages.append({"role": "assistant", "content": answer})
    session.updated_at = datetime.now().isoformat()
    if len(session.messages) == 2 and session.title == "New chat":
        first = next((m["content"] for m in session.messages if m["role"] == "user"), "")
        session.title = first[:50] + ("..." if len(first) > 50 else "")
    _get_client().table(TABLE).update({
        "messages": session.messages,
        "title": session.title,
        "updated_at": session.updated_at,
    }).eq("id", session_id).eq("owner_id", owner_id).execute()
    return session


def update_session_pdf(session_id: str, owner_id: str, pdf_session_id: str, filenames: list[str]):
    session = load_session(session_id, owner_id)
    if not session:
        return
    title = filenames[0] if filenames and session.title == "New chat" else session.title
    _get_client().table(TABLE).update({
        "session_id": pdf_session_id, "documents": filenames,
        "title": title, "updated_at": datetime.now().isoformat(),
    }).eq("id", session_id).eq("owner_id", owner_id).execute()
    logger.info(f"Linked PDF session {pdf_session_id} → chat {session_id}")


def delete_session(session_id: str, owner_id: str) -> bool:
    session = load_session(session_id, owner_id)
    if not session:
        return False
    _get_client().table(TABLE).delete().eq("id", session_id).eq("owner_id", owner_id).execute()
    # The FAISS index is keyed by the PDF session id stored on the chat row, not the chat id.
    if session.session_id:
        _get_client().table("faiss_indexes").delete().eq(
            "session_id", session.session_id
        ).eq("owner_id", owner_id).execute()
    logger.info(f"Deleted session: {session_id}")
    return True


def save_document(chat_session_id: str, filename: str, file_bytes: bytes):
    logger.info(f"Document tracked: {filename} for session {chat_session_id}")


# ── FAISS persistence ─────────────────────────────────────────────────────

def save_faiss_index(session_id: str, owner_id: str, index_bytes: bytes):
    b64 = base64.b64encode(index_bytes).decode("utf-8")
    _get_client().table("faiss_indexes").upsert({
        "session_id": session_id,
        "owner_id": owner_id,
        "index_b64": b64,
        "updated_at": datetime.now().isoformat(),
    }).execute()
    logger.info(f"FAISS index saved: {session_id}")


def load_faiss_index(session_id: str, owner_id: str) -> bytes | None:
    res = _get_client().table("faiss_indexes").select("index_b64").eq(
        "session_id", session_id
    ).eq("owner_id", owner_id).execute()
    if not res.data:
        return None
    logger.info(f"FAISS index loaded: {session_id}")
    return base64.b64decode(res.data[0]["index_b64"])


def faiss_index_exists(session_id: str, owner_id: str) -> bool:
    res = _get_client().table("faiss_indexes").select("session_id").eq(
        "session_id", session_id
    ).eq("owner_id", owner_id).execute()
    return bool(res.data)