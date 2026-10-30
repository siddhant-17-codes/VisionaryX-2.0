import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.logger import setup_logger
from config.settings import get_settings
from core.exceptions import VisionaryXError
from routers import chat_router, generate_router, image_router, pdf_router
from routers.deps import MAX_REQUEST_BYTES
from routers.sessions import router as sessions_router

settings = get_settings()
logger = setup_logger("visionaryx.main")


os.makedirs("logs", exist_ok=True)

app = FastAPI(
    title="VisionaryX 2.0 API",
    description="Intelligent document querying, image analysis, and AI generation platform.",
    version="2.0.0",
)


# Registered before CORS so CORS wraps it and the browser can read the 413 body.
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_REQUEST_BYTES:
        return JSONResponse(
            status_code=413,
            content={"error": f"Request is larger than {MAX_REQUEST_BYTES // (1024 * 1024)} MB.",
                     "type": "FileTooLargeError"},
        )
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.exception_handler(VisionaryXError)
async def visionaryx_error_handler(request: Request, exc: VisionaryXError):
    logger.error(f"VisionaryXError on {request.url.path}: {exc.message}")
    retry_after = getattr(exc, "retry_after", None)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "type": type(exc).__name__},
        headers={"Retry-After": str(retry_after)} if retry_after else None,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(part) for part in first.get("loc", ())[1:]) or "request"
    return JSONResponse(
        status_code=422,
        content={"error": f"Invalid {field}: {first.get('msg', 'bad value')}.", "type": "ValidationError"},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again.", "type": "InternalServerError"},
    )


app.include_router(chat_router)
app.include_router(pdf_router)
app.include_router(image_router)
app.include_router(generate_router)
app.include_router(sessions_router)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "version": "2.0.0"}