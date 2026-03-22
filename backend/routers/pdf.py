import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from models.schemas import PDFQueryRequest, PDFQueryResponse
from services.rag_service import process_files, query_documents

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

SUPPORTED_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
}


class UploadResponse(BaseModel):
    session_id: str
    questions: list[str]
    files_processed: int


@router.post("/upload", response_model=UploadResponse)
async def upload_files(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")

    session_id = str(uuid.uuid4())
    file_data: list[tuple[bytes, str]] = []

    for f in files:
        if f.content_type not in SUPPORTED_TYPES and not (
            f.filename.endswith(".pdf") or
            f.filename.endswith(".docx") or
            f.filename.endswith(".doc")
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file: {f.filename}. Upload PDF or DOCX files only."
            )
        file_data.append((await f.read(), f.filename))

    questions = process_files(session_id, file_data)
    return UploadResponse(
        session_id=session_id,
        questions=questions,
        files_processed=len(file_data),
    )


@router.post("/query", response_model=PDFQueryResponse)
async def query_pdf(request: PDFQueryRequest):
    return query_documents(request.session_id, request.question, request.history)