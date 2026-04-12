import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from models.schemas import PDFQueryResponse, ChatMessage
from services.rag_service import process_files, query_documents
from core.storage import update_session_pdf, append_message, save_document
from config.logger import setup_logger

router = APIRouter(prefix="/api/pdf", tags=["pdf"])
logger = setup_logger("visionaryx.pdf_router")

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc"}


class UploadResponse(BaseModel):
    session_id: str
    questions: list[str]
    files_processed: int


class PersistentPDFQueryRequest(BaseModel):
    question: str
    session_id: str
    history: list = []
    chat_session_id: Optional[str] = None


@router.post("/upload", response_model=UploadResponse)
@router.post("/upload", response_model=UploadResponse)
async def upload_files(
    files: list[UploadFile] = File(...),
    chat_session_id: Optional[str] = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

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
        file_bytes = await f.read()
        file_data.append((file_bytes, f.filename))
        filenames.append(f.filename)

        if chat_session_id:
            save_document(chat_session_id, f.filename, file_bytes)

    questions = process_files(session_id, file_data)

    if chat_session_id:
        update_session_pdf(chat_session_id, session_id, filenames)
        logger.info(f"Linked PDF session {session_id} to chat session {chat_session_id}")

    return UploadResponse(
        session_id=session_id,
        questions=questions,
        files_processed=len(file_data),
    )


@router.post("/query", response_model=PDFQueryResponse)
async def query_pdf(request: PersistentPDFQueryRequest):
    history = [ChatMessage(**m) if isinstance(m, dict) else m for m in request.history]
    result = query_documents(request.session_id, request.question, history)

    if request.chat_session_id:
        append_message(request.chat_session_id, "user", request.question)
        append_message(request.chat_session_id, "assistant", result.answer)
        logger.debug(f"Persisted PDF Q&A to session: {request.chat_session_id}")

    return result