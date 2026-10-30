from functools import lru_cache

from google.genai import types
from langchain_core.embeddings import Embeddings

from core.genai_client import get_client

# Must stay the same model, task types and (default) dimension that
# langchain-google-genai 2.0.10 used, or PDF indexes built before the move to
# google-genai stop matching new questions.
EMBEDDING_MODEL = "gemini-embedding-001"
DOCUMENT_TASK = "RETRIEVAL_DOCUMENT"
QUERY_TASK = "RETRIEVAL_QUERY"
# Same batching as before: at most 100 texts and ~20k tokens per request.
MAX_BATCH_TEXTS = 100
MAX_BATCH_TOKENS = 20_000


def _batches(texts: list[str]) -> list[list[str]]:
    batches, current, tokens = [], [], 0
    for text in texts:
        cost = len(text) // 4 + 1  # rough token estimate
        if current and (len(current) == MAX_BATCH_TEXTS or tokens + cost > MAX_BATCH_TOKENS):
            batches.append(current)
            current, tokens = [], 0
        current.append(text)
        tokens += cost
    if current:
        batches.append(current)
    return batches


class GeminiEmbeddings(Embeddings):
    """LangChain embeddings backed by google-genai, for the FAISS store."""

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        vectors: list[list[float]] = []
        for batch in _batches(texts):
            result = get_client().models.embed_content(
                model=EMBEDDING_MODEL, contents=batch, config=types.EmbedContentConfig(task_type=task_type),
            )
            vectors.extend(e.values for e in result.embeddings)
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts, DOCUMENT_TASK)

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], QUERY_TASK)[0]


@lru_cache
def get_embeddings() -> GeminiEmbeddings:
    return GeminiEmbeddings()
