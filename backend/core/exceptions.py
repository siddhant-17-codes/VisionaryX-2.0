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
    """Raised when a Gemini call fails for a reason not covered below. The upstream
    text is logged, never returned: it can contain request details."""
    def __init__(self, message: str):
        super().__init__("The AI model could not answer this request. Please try again.", status_code=502)
        self.detail = message


class LLMQuotaError(VisionaryXError):
    """Raised when every Gemini model in the fallback chain is out of quota."""
    def __init__(self):
        super().__init__(
            "The AI model's free daily quota is used up. It resets at midnight Pacific time.",
            status_code=429,
        )


class LLMUnavailableError(VisionaryXError):
    """Raised when every Gemini model in the chain is overloaded or not found."""
    def __init__(self):
        super().__init__("The AI model is temporarily unavailable. Please try again shortly.", status_code=503)


class UpstreamTimeoutError(VisionaryXError):
    """Raised when Gemini or Hugging Face does not answer in time."""
    def __init__(self):
        super().__init__("The AI service took too long to respond. Please try again.", status_code=504)


class RateLimitError(VisionaryXError):
    """Raised when one client sends too many requests in a short window."""
    def __init__(self, retry_after: int):
        super().__init__(f"Too many requests. Please wait {retry_after}s and retry.", status_code=429)
        self.retry_after = retry_after


class FileTooLargeError(VisionaryXError):
    """Raised when an upload is over the size or count limit."""
    def __init__(self, message: str):
        super().__init__(message, status_code=413)


class InvalidImageError(VisionaryXError):
    """Raised when an uploaded image cannot be decoded."""
    def __init__(self):
        super().__init__("That file is not a readable image. Upload a PNG, JPEG, WebP or GIF.", status_code=400)


class ImageGenerationError(VisionaryXError):
    """Raised when image generation fails."""
    def __init__(self, message: str):
        super().__init__("Image generation failed. Please try again.", status_code=502)
        self.detail = message


class ImageQuotaExceededError(VisionaryXError):
    """Raised when every image provider's free quota is used up. retry_after is the
    number of seconds until it is expected back (sent as Retry-After)."""
    def __init__(self, retry_after: int):
        super().__init__(
            "Image generation is paused: the free image quota is used up for now. Please try again later.",
            status_code=503,
        )
        self.retry_after = retry_after


class UnsupportedFileTypeError(VisionaryXError):
    """Raised when an unsupported file is uploaded."""
    def __init__(self, filename: str):
        super().__init__(
            f"Unsupported file type: '{filename}'. Only PDF and DOCX are supported.",
            status_code=415,
        )