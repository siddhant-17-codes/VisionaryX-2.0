import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from config.logger import setup_logger
from core.exceptions import FileTooLargeError
from core.rate_limit import gemini_limit, upload_limit
from core.storage import append_turn, save_document, update_session_pdf
from models.schemas import History, PDFQueryResponse, SessionRef, UserText
from routers.deps import MAX_DOCUMENT_BYTES, MAX_DOCUMENTS, owned_session, owner_id, read_capped
from services.rag_service import process_files, query_documents

router = APIRouter(prefix="/api/pdf", tags=["pdf"])
logger = setup_logger("visionaryx.pdf_router")

# Legacy .doc (binary Word 97) can't be parsed by python-docx, so it is refused up front.
SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class UploadResponse(BaseModel):
    session_id: str
    questions: list[str]
    files_processed: int


class PersistentPDFQueryRequest(BaseModel):
    question: UserText
    session_id: SessionRef
    history: History = []
    chat_session_id: SessionRef | None = None


@router.post("/upload", response_model=UploadResponse)
@router.post("/upload", response_model=UploadResponse)
def upload_files(
    _: None = Depends(upload_limit),
    files: list[UploadFile] = File(...),
    chat_session_id: str | None = Form(None, max_length=64),
    owner: str = Depends(owner_id),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
    if len(files) > MAX_DOCUMENTS:
        raise FileTooLargeError(f"Upload at most {MAX_DOCUMENTS} files at a time.")
    chat_session = owned_session(chat_session_id, owner)

    session_id = str(uuid.uuid4())
    file_data = []
    filenames = []

    for f in files:
        ext = "." + f.filename.rsplit(".", 1)[-1].lower() if "." in f.filename else ""
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file: {f.filename}. Upload PDF or DOCX only."
            )
        file_bytes = read_capped(f, MAX_DOCUMENT_BYTES)
        file_data.append((file_bytes, f.filename))
        filenames.append(f.filename)

        if chat_session_id:
            save_document(chat_session_id, f.filename, file_bytes)

    questions = process_files(session_id, owner, file_data)

    if chat_session:
        update_session_pdf(chat_session, session_id, filenames)
        logger.info(f"Linked PDF session {session_id} to chat session {chat_session_id}")

    return UploadResponse(
        session_id=session_id,
        questions=questions,
        files_processed=len(file_data),
    )


@router.post("/query", response_model=PDFQueryResponse, dependencies=[Depends(gemini_limit)])
def query_pdf(request: PersistentPDFQueryRequest, owner: str = Depends(owner_id)):
    chat_session = owned_session(request.chat_session_id, owner)
    result = query_documents(request.session_id, owner, request.question, request.history)

    if chat_session:
        append_turn(chat_session, request.question, result.answer)
        logger.debug(f"Persisted PDF Q&A to session: {request.chat_session_id}")

    return result
