from fastapi import APIRouter, Depends, File, Form, UploadFile

from core.rate_limit import gemini_limit
from models.schemas import ImageQueryResponse
from routers.deps import MAX_IMAGE_BYTES, read_capped
from services.gemini_service import analyze_image

router = APIRouter(prefix="/api/image", tags=["image"])


@router.post("/query", response_model=ImageQueryResponse, dependencies=[Depends(gemini_limit)])
def query_image(
    file: UploadFile = File(...),
    prompt: str = Form(default="Describe this image in detail.", min_length=1, max_length=1000),
):
    image_bytes = read_capped(file, MAX_IMAGE_BYTES)
    generated = analyze_image(image_bytes, prompt)
    return ImageQueryResponse(answer=generated.text, model=generated.model)
