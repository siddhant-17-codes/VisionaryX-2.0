import os
import pickle
import tempfile
from langchain_community.vectorstores import FAISS
from core.storage import save_faiss_index, load_faiss_index, faiss_index_exists
from config.logger import setup_logger

logger = setup_logger("visionaryx.vector_store")


def _get_embeddings():
    from core.embeddings import get_embeddings
    return get_embeddings()


def build_vector_store(session_id: str, files: list[tuple[bytes, str]]):
    from core.chunker import extract_chunks_from_file
    all_chunks = []
    for file_bytes, filename in files:
        chunks = extract_chunks_from_file(file_bytes, filename)
        all_chunks.extend(chunks)
        logger.debug(f"Chunked {filename}: {len(chunks)} chunks")

    embeddings = _get_embeddings()
    store = FAISS.from_documents(all_chunks, embeddings)
    index_bytes = _serialize_store(store)
    save_faiss_index(session_id, index_bytes)
    logger.info(f"Built and persisted FAISS index: {session_id} | {len(all_chunks)} chunks")


def load_vector_store(session_id: str) -> FAISS:
    index_bytes = load_faiss_index(session_id)
    if not index_bytes:
        raise ValueError(f"No FAISS index found for session: {session_id}")
    store = _deserialize_store(index_bytes)
    logger.info(f"Loaded FAISS index: {session_id}")
    return store


def session_exists(session_id: str) -> bool:
    return faiss_index_exists(session_id)


def _serialize_store(store: FAISS) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        store.save_local(tmp)
        with open(os.path.join(tmp, "index.faiss"), "rb") as f:
            idx_bytes = f.read()
        with open(os.path.join(tmp, "index.pkl"), "rb") as f:
            pkl_bytes = f.read()
    return pickle.dumps({"idx": idx_bytes, "pkl": pkl_bytes})


def _deserialize_store(data: bytes) -> FAISS:
    payload = pickle.loads(data)
    embeddings = _get_embeddings()
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "index.faiss"), "wb") as f:
            f.write(payload["idx"])
        with open(os.path.join(tmp, "index.pkl"), "wb") as f:
            f.write(payload["pkl"])
        store = FAISS.load_local(
            tmp, embeddings, allow_dangerous_deserialization=True
        )
    return store