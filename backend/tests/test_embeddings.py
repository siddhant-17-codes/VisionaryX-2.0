"""D4: embeddings must match what langchain-google-genai 2.0.10 sent, so PDF indexes
built before the move to google-genai keep matching new questions."""
from types import SimpleNamespace

import pytest

from core import embeddings


class FakeModels:
    def __init__(self):
        self.calls = []

    def embed_content(self, model, contents, config):
        self.calls.append((model, list(contents), config.task_type, config.output_dimensionality))
        return SimpleNamespace(embeddings=[SimpleNamespace(values=[float(len(t))]) for t in contents])


@pytest.fixture
def models(monkeypatch):
    fake = FakeModels()
    monkeypatch.setattr(embeddings, "get_client", lambda: SimpleNamespace(models=fake))
    return fake


def test_documents_and_queries_use_the_same_model_and_task_types_as_before(models):
    store = embeddings.GeminiEmbeddings()
    assert store.embed_documents(["ab", "abc"]) == [[2.0], [3.0]]
    assert store.embed_query("abcd") == [4.0]
    assert models.calls == [
        ("gemini-embedding-001", ["ab", "abc"], "RETRIEVAL_DOCUMENT", None),  # None = default dimension
        ("gemini-embedding-001", ["abcd"], "RETRIEVAL_QUERY", None),
    ]


def test_large_uploads_are_batched_and_keep_their_order(models):
    texts = [f"chunk {i} " + "x" * 2000 for i in range(250)]
    vectors = embeddings.GeminiEmbeddings().embed_documents(texts)
    assert vectors == [[float(len(t))] for t in texts]
    sizes = [len(call[1]) for call in models.calls]
    assert sum(sizes) == 250
    assert max(sizes) <= embeddings.MAX_BATCH_TEXTS
    assert all(sum(len(t) // 4 + 1 for t in call[1]) <= embeddings.MAX_BATCH_TOKENS for call in models.calls)
