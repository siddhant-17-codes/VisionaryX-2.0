from functools import lru_cache

from google import genai
from google.genai import types

from config.settings import get_settings

# Seconds per Gemini request. Three chat attempts stay inside the frontend's 120s timeout.
LLM_TIMEOUT = 30
# Our fallback chain is the retry policy, so the SDK's own retries are switched off.
HTTP_OPTIONS = types.HttpOptions(timeout=LLM_TIMEOUT * 1000, retry_options=types.HttpRetryOptions(attempts=1))


@lru_cache
def get_client() -> genai.Client:
    """One google-genai client (and connection pool) for chat, vision and embeddings."""
    return genai.Client(api_key=get_settings().google_api_key, http_options=HTTP_OPTIONS)
