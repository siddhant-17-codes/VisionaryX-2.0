class VisionaryXError(Exception):
    """Base exception for VisionaryX."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DocumentProcessingError(VisionaryXError):
    """Raised when PDF/DOCX processing fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)


class SessionNotFoundError(VisionaryXError):
    """Raised when a RAG session does not exist."""
    def __init__(self, session_id: str):
        super().__init__(
            f"Session '{session_id}' not found. Please upload documents first.",
            status_code=404,
        )


class EmbeddingError(VisionaryXError):
    """Raised when vector embedding fails."""
    def __init__(self, message: str):
        super().__init__(f"Embedding failed: {message}", status_code=502)


class LLMError(VisionaryXError):
    """Raised when Gemini API call fails."""
    def __init__(self, message: str):
        super().__init__(f"LLM error: {message}", status_code=502)


class ImageGenerationError(VisionaryXError):
    """Raised when image generation fails."""
    def __init__(self, message: str):
        super().__init__(f"Image generation failed: {message}", status_code=502)


class UnsupportedFileTypeError(VisionaryXError):
    """Raised when an unsupported file is uploaded."""
    def __init__(self, filename: str):
        super().__init__(
            f"Unsupported file type: '{filename}'. Only PDF and DOCX are supported.",
            status_code=415,
        )