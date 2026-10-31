"""How a FAISS store is saved in Supabase, without pickle (S4).

Format 1 (written from now on) is JSON: the raw FAISS index (base64) plus each
document's text and metadata. Nothing in it can run code when loaded.

Indexes saved before this were pickles: an outer dict holding LangChain's
index.faiss bytes and its index.pkl (docstore + id map). They are still read, by a
data-only unpickler that maps the only two classes they contain to inert stand-ins
and refuses everything else, so a tampered row can't execute anything.
"""
import base64
import io
import json
import pickle

import faiss
import numpy as np
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

FORMAT = "visionaryx-faiss/1"


def dumps(store: FAISS) -> bytes:
    ids = [store.index_to_docstore_id[i] for i in range(store.index.ntotal)]
    docs = {}
    for doc_id in ids:
        doc = store.docstore.search(doc_id)
        docs[doc_id] = {"text": doc.page_content, "metadata": doc.metadata}
    payload = {
        "format": FORMAT,
        "index": base64.b64encode(faiss.serialize_index(store.index).tobytes()).decode("ascii"),
        "ids": ids,
        "docs": docs,
    }
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def loads(data: bytes, embeddings: Embeddings) -> FAISS:
    if data[:1] == b"{":
        payload = json.loads(data)
        if payload.get("format") != FORMAT:
            raise ValueError(f"Unknown FAISS index format: {payload.get('format')!r}")
        index_bytes = base64.b64decode(payload["index"])
        ids = payload["ids"]
        docs = payload["docs"]
    else:
        index_bytes, ids, docs = _read_legacy(data)
    index = faiss.deserialize_index(np.frombuffer(index_bytes, dtype=np.uint8))
    docstore = InMemoryDocstore({
        doc_id: Document(page_content=d["text"], metadata=d["metadata"]) for doc_id, d in docs.items()
    })
    return FAISS(embedding_function=embeddings, index=index, docstore=docstore,
                 index_to_docstore_id=dict(enumerate(ids)))


# ── Legacy (pickled) indexes ────────────────────────────────────────────────────

class _Captured:
    """Stand-in for an allowed class: records the pickled state, runs no class code."""

    def __setstate__(self, state):
        self.state = state


class _Docstore(_Captured):
    pass


class _Document(_Captured):
    pass


_ALLOWED = {
    ("langchain_community.docstore.in_memory", "InMemoryDocstore"): _Docstore,
    ("langchain_core.documents.base", "Document"): _Document,
}


class _DataOnlyUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        try:
            return _ALLOWED[(module, name)]
        except KeyError:
            raise pickle.UnpicklingError(f"Refusing to load {module}.{name} from a stored index") from None


def _unpickle(data: bytes):
    return _DataOnlyUnpickler(io.BytesIO(data)).load()


def _fields(captured: _Captured) -> dict:
    # pydantic models pickle as {"__dict__": fields, ...}; plain objects as their __dict__.
    state = captured.state
    return state.get("__dict__", state)


def _read_legacy(data: bytes) -> tuple[bytes, list[str], dict]:
    outer = _unpickle(data)
    if not isinstance(outer, dict) or not all(isinstance(outer.get(k), bytes) for k in ("idx", "pkl")):
        raise ValueError("Stored index is not in the expected legacy format")
    docstore, index_to_id = _unpickle(outer["pkl"])
    if not isinstance(docstore, _Docstore) or not isinstance(index_to_id, dict):
        raise ValueError("Stored index is not in the expected legacy format")
    docs = {}
    for doc_id, doc in _fields(docstore)["_dict"].items():
        if not isinstance(doc, _Document):
            raise ValueError("Stored index is not in the expected legacy format")
        fields = _fields(doc)
        docs[doc_id] = {"text": fields["page_content"], "metadata": dict(fields.get("metadata") or {})}
    ids = [index_to_id[i] for i in range(len(index_to_id))]
    return outer["idx"], ids, docs
