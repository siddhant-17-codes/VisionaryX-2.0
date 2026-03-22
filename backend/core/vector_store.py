import os
import pickle
from langchain_community.vectorstores import FAISS
from .chunker import Chunk, extract_chunks_from_file
from .embeddings import get_embeddings

STORE_DIR = "faiss_index"


def build_vector_store(session_id: str, files: list[tuple[bytes, str]]) -> None:
    all_chunks: list[Chunk] = []
    for file_bytes, filename in files:
        all_chunks.extend(extract_chunks_from_file(file_bytes, filename))

    texts = [c.text for c in all_chunks]
    metadatas = [{"page": c.page, "chunk_index": c.chunk_index} for c in all_chunks]

    embeddings = get_embeddings()
    store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    session_path = os.path.join(STORE_DIR, session_id)
    os.makedirs(session_path, exist_ok=True)
    store.save_local(session_path)

    with open(os.path.join(session_path, "chunks.pkl"), "wb") as f:
        pickle.dump(all_chunks, f)


def load_vector_store(session_id: str) -> FAISS:
    session_path = os.path.join(STORE_DIR, session_id)
    embeddings = get_embeddings()
    return FAISS.load_local(
        session_path, embeddings, allow_dangerous_deserialization=True
    )


def session_exists(session_id: str) -> bool:
    return os.path.exists(os.path.join(STORE_DIR, session_id, "index.faiss"))