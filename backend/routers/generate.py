from fastapi import APIRouter, Depends

from core.rate_limit import generate_limit
from models.schemas import GenerateImageRequest, GenerateImageResponse
from services.image_service import generate_image

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("/image", response_model=GenerateImageResponse, dependencies=[Depends(generate_limit)])
def generate(request: GenerateImageRequest):
    image_b64 = generate_image(request.prompt)
    return GenerateImageResponse(image_base64=image_b64)
