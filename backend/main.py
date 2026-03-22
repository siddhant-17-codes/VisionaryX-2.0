import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.settings import get_settings
from config.logger import setup_logger
from core.exceptions import VisionaryXError
from routers import chat_router, pdf_router, image_router, generate_router

settings = get_settings()
logger = setup_logger("visionaryx.main")

app = FastAPI(
    title="VisionaryX 2.0 API",
    description="Intelligent document querying, image analysis, and AI generation platform.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request logging middleware ─────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    logger.info(f"[{request_id}] --> {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"[{request_id}] <-- {request.method} {request.url.path} "
        f"| status={response.status_code} | {duration}ms"
    )
    return response


# ── Global exception handlers ──────────────────────────────────────────────
@app.exception_handler(VisionaryXError)
async def visionaryx_error_handler(request: Request, exc: VisionaryXError):
    logger.error(f"VisionaryXError on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": type(exc).__name__},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred. Please try again.",
            "type": "InternalServerError",
        },
    )


# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(pdf_router)
app.include_router(image_router)
app.include_router(generate_router)


@app.get("/health", tags=["system"])
async def health():
    logger.info("Health check requested")
    return {"status": "ok", "version": "2.0.0"}