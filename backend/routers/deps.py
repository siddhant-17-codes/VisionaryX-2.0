import hashlib
import re

from fastapi import Header, HTTPException, UploadFile

from core.exceptions import FileTooLargeError

MB = 1024 * 1024
MAX_DOCUMENTS = 5
MAX_DOCUMENT_BYTES = 10 * MB
MAX_IMAGE_BYTES = 8 * MB
# Whole-request cap checked from Content-Length before the body is parsed.
MAX_REQUEST_BYTES = MAX_DOCUMENTS * MAX_DOCUMENT_BYTES + MB


async def read_capped(upload: UploadFile, max_bytes: int) -> bytes:
    """Read an upload, refusing it as soon as it passes max_bytes."""
    data = await upload.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise FileTooLargeError(f"{upload.filename} is larger than {max_bytes // MB} MB.")
    return data

_CLIENT_ID = re.compile(r"[A-Za-z0-9_-]{16,64}")


def owner_id(x_client_id: str | None = Header(None)) -> str:
    """Anonymous owner key. The browser generates a random id once, keeps it in
    localStorage and sends it on every call; sessions are only visible to that id.
    Only its SHA-256 is stored, so a database leak does not hand out working ids."""
    if not x_client_id or not _CLIENT_ID.fullmatch(x_client_id):
        raise HTTPException(status_code=400, detail="Missing or invalid X-Client-Id header.")
    return hashlib.sha256(x_client_id.encode()).hexdigest()
