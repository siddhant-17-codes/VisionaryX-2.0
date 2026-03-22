from pydantic import BaseModel
from typing import Optional


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


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
    page: int
    chunk: str


class PDFQueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class SuggestedQuestionsResponse(BaseModel):
    questions: list[str]


class ImageQueryRequest(BaseModel):
    prompt: Optional[str] = "Describe this image in detail."


class ImageQueryResponse(BaseModel):
    answer: str


class GenerateImageRequest(BaseModel):
    prompt: str


class GenerateImageResponse(BaseModel):
    image_base64: str
