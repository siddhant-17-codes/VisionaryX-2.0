from langchain_google_genai import GoogleGenerativeAIEmbeddings
from functools import lru_cache
from config.settings import get_settings


@lru_cache()
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    settings = get_settings()
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.google_api_key,
    )