from fastapi import APIRouter, UploadFile, File, Form
from models.schemas import ImageQueryResponse
from services.gemini_service import analyze_image

router = APIRouter(prefix="/api/image", tags=["image"])


@router.post("/query", response_model=ImageQueryResponse)
async def query_image(
    file: UploadFile = File(...),
    prompt: str = Form(default="Describe this image in detail."),
):
    image_bytes = await file.read()
    answer = analyze_image(image_bytes, prompt)
    return ImageQueryResponse(answer=answer)
