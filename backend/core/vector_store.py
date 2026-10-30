from langchain_community.vectorstores import FAISS

from config.logger import setup_logger
from core import faiss_codec
from core.chunker import Chunk
from core.storage import faiss_index_exists, load_faiss_index, save_faiss_index

logger = setup_logger("visionaryx.vector_store")


def _get_embeddings():
    from core.embeddings import get_embeddings
    return get_embeddings()

def build_vector_store(session_id: str, owner_id: str, files: list[tuple[str, list[Chunk]]]):
    """Index already-extracted chunks: (filename, chunks) per file."""
    from langchain.schema import Document

    all_docs = []
    for filename, chunks in files:
        for chunk in chunks:
            all_docs.append(Document(
                page_content=chunk.text,
                metadata={"source": filename, "page": chunk.page, "section": chunk.section,
                          "chunk_index": chunk.chunk_index}
            ))
        logger.debug(f"Chunked {filename}: {len(chunks)} chunks")

    embeddings = _get_embeddings()
    store = FAISS.from_documents(all_docs, embeddings)
    index_bytes = _serialize_store(store)
    save_faiss_index(session_id, owner_id, index_bytes)
    logger.info(f"Built and persisted FAISS index: {session_id} | {len(all_docs)} docs")


def load_vector_store(session_id: str, owner_id: str) -> FAISS:
    index_bytes = load_faiss_index(session_id, owner_id)
    if not index_bytes:
        raise ValueError(f"No FAISS index found for session: {session_id}")
    store = _deserialize_store(index_bytes)
    logger.info(f"Loaded FAISS index: {session_id}")
    return store


def session_exists(session_id: str, owner_id: str) -> bool:
    return faiss_index_exists(session_id, owner_id)


def _serialize_store(store: FAISS) -> bytes:
    return faiss_codec.dumps(store)


def _deserialize_store(data: bytes) -> FAISS:
    return faiss_codec.loads(data, _get_embeddings())
