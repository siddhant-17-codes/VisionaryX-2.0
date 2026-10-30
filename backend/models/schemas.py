
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, StringConstraints

# Limits on what a client may send. Blank or oversized input is rejected with 422
# before any model call is made.
MAX_MESSAGE_CHARS = 20_000  # roughly 5k tokens; long pasted passages still fit
MAX_HISTORY_MESSAGES = 40

UserText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_MESSAGE_CHARS)]
ImagePrompt = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
SessionRef = Annotated[str, StringConstraints(min_length=1, max_length=64)]


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: Annotated[str, StringConstraints(max_length=50_000)]


def _keep_recent(history: list[ChatMessage]) -> list[ChatMessage]:
    # The frontend sends the whole conversation; long chats keep working on the
    # most recent turns instead of failing validation.
    return history[-MAX_HISTORY_MESSAGES:]


History = Annotated[list[ChatMessage], AfterValidator(_keep_recent)]


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


class PDFQueryRequest(BaseModel):
    question: str
    session_id: str
    history: list[ChatMessage] = []


class Citation(BaseModel):
    # File the chunk came from. None for indexes built before sources were stored.
    source: str | None = None
    page: int  # 0 for DOCX, which has no pages
    section: str | None = None  # DOCX heading, when there is one
    chunk: str


class PDFQueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class SuggestedQuestionsResponse(BaseModel):
    questions: list[str]


class ImageQueryRequest(BaseModel):
    prompt: str | None = "Describe this image in detail."


class ImageQueryResponse(BaseModel):
    answer: str


class GenerateImageRequest(BaseModel):
    prompt: ImagePrompt


class GenerateImageResponse(BaseModel):
    image_base64: str
