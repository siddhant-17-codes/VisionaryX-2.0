import re

from fastapi import Header, HTTPException

_CLIENT_ID = re.compile(r"[A-Za-z0-9_-]{16,64}")


def client_id(x_client_id: str | None = Header(None)) -> str:
    """Anonymous owner key. The browser generates a random id once, keeps it in
    localStorage and sends it on every call; sessions are only visible to that id."""
    if not x_client_id or not _CLIENT_ID.fullmatch(x_client_id):
        raise HTTPException(status_code=400, detail="Missing or invalid X-Client-Id header.")
    return x_client_id
