"""S4: FAISS indexes are stored without pickle; legacy pickled rows still load, but
only as data."""
import os
import pickle
import tempfile

import numpy as np
import pytest
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding

from core import faiss_codec

EMB = DeterministicFakeEmbedding(size=16)
DOCS = [
    Document(page_content="Apple harvest was 1,870 tonnes.",
             metadata={"source": "a.pdf", "page": 2, "chunk_index": 0}),
    Document(page_content="Shifts run Tuesday to Saturday.",
             metadata={"source": "h.docx", "page": 0, "section": "Shifts"}),
    Document(page_content="Lost items are kept for 30 days.", metadata={"page": 1}),
]


def store() -> FAISS:
    return FAISS.from_documents(DOCS, EMB)


def legacy_blob(s: FAISS) -> bytes:
    """Exactly what the backend stored before S4."""
    with tempfile.TemporaryDirectory() as tmp:
        s.save_local(tmp)
        idx = open(os.path.join(tmp, "index.faiss"), "rb").read()
        pkl = open(os.path.join(tmp, "index.pkl"), "rb").read()
    return pickle.dumps({"idx": idx, "pkl": pkl})


def snapshot(s: FAISS):
    ids = [s.index_to_docstore_id[i] for i in range(s.index.ntotal)]
    docs = [(s.docstore.search(i).page_content, s.docstore.search(i).metadata) for i in ids]
    return ids, docs, s.index.reconstruct_n(0, s.index.ntotal)


def assert_same(a: FAISS, b: FAISS):
    ids_a, docs_a, vec_a = snapshot(a)
    ids_b, docs_b, vec_b = snapshot(b)
    assert ids_a == ids_b and docs_a == docs_b
    np.testing.assert_array_equal(vec_a, vec_b)
    def hits(s: FAISS):
        results = s.similarity_search_with_score("how long are lost items kept?", k=3)
        return [(d.page_content, round(float(score), 6)) for d, score in results]
    assert hits(a) == hits(b)


def test_new_format_round_trips_and_contains_no_pickle():
    original = store()
    data = faiss_codec.dumps(original)
    assert data.startswith(b"{") and b"visionaryx-faiss/1" in data
    assert_same(original, faiss_codec.loads(data, EMB))


def test_indexes_saved_before_s4_still_load_identically():
    original = store()
    assert_same(original, faiss_codec.loads(legacy_blob(original), EMB))


class _Evil:
    def __init__(self, marker):
        self.marker = marker

    def __reduce__(self):
        return (open, (self.marker, "w"))  # would create a file if ever executed


def test_a_tampered_inner_pickle_is_refused_without_running(tmp_path):
    marker = str(tmp_path / "ran")
    blob = pickle.dumps({"idx": b"x", "pkl": pickle.dumps((_Evil(marker), {}))})
    with pytest.raises(pickle.UnpicklingError, match="Refusing to load"):
        faiss_codec.loads(blob, EMB)
    assert not os.path.exists(marker)


def test_a_tampered_outer_pickle_is_refused_without_running(tmp_path):
    marker = str(tmp_path / "ran")
    with pytest.raises(pickle.UnpicklingError, match="Refusing to load"):
        faiss_codec.loads(pickle.dumps(_Evil(marker)), EMB)
    assert not os.path.exists(marker)


def test_unknown_json_format_is_refused():
    with pytest.raises(ValueError, match="Unknown FAISS index format"):
        faiss_codec.loads(b'{"format": "something-else"}', EMB)


def test_upload_stores_the_new_format(client, supabase):
    from tests.conftest import fixture_bytes
    res = client.post("/api/pdf/upload", files=[
        ("files", ("lumen_ridge_report.pdf", fixture_bytes("lumen_ridge_report.pdf"), "application/pdf"))])
    assert res.status_code == 200
    # Stored as the codec's JSON text, with no extra base64 layer (2.0.1).
    stored = supabase.db["faiss_indexes"][0]["index_b64"]
    assert stored.startswith('{"format": "visionaryx-faiss/1"')
