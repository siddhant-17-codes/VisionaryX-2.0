from fastapi import APIRouter, Depends
from pydantic import BaseModel

from core.rate_limit import generate_daily_limit, generate_limit
from models.schemas import GenerateImageRequest, GenerateImageResponse
from services.image_service import generate_image, pause_status

router = APIRouter(prefix="/api/generate", tags=["generate"])


class GenerateStatusResponse(BaseModel):
    available: bool
    resumes_at: str | None = None  # ISO-8601 UTC, when paused


@router.post("/image", response_model=GenerateImageResponse,
             dependencies=[Depends(generate_limit), Depends(generate_daily_limit)])
def generate(request: GenerateImageRequest):
    image_b64 = generate_image(request.prompt)
    return GenerateImageResponse(image_base64=image_b64)


@router.get("/status", response_model=GenerateStatusResponse)
def status():
    """Lets the page say "paused" before anyone types a prompt. Costs no quota."""
    paused_until = pause_status()
    if paused_until:
        return GenerateStatusResponse(available=False, resumes_at=paused_until.isoformat())
    return GenerateStatusResponse(available=True)
