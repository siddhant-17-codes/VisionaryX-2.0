from config.logger import setup_logger
from core.vector_store import build_vector_store, load_vector_store, session_exists
from core.chunker import extract_chunks_from_file
from core.exceptions import SessionNotFoundError, DocumentProcessingError
from services.gemini_service import query_with_context, suggest_questions
from models.schemas import ChatMessage, Citation, PDFQueryResponse

logger = setup_logger("visionaryx.rag")


def _adaptive_threshold(scores: list[float]) -> float:
    """
    Compute an adaptive relevance threshold based on score distribution.
    FAISS L2 distances: lower = more similar.
    Strategy: accept chunks within 40% above the best (lowest) score.
    Falls back to a generous absolute cap of 2.0 if best score is very low.
    """
    if not scores:
        return 2.0
    best = min(scores)
    threshold = best * 1.4
    return min(threshold, 2.0)


def process_files(session_id: str, files: list[tuple[bytes, str]]) -> list[str]:
    try:
        logger.info(f"Processing {len(files)} file(s) for session={session_id}")
        build_vector_store(session_id, files)
        combined_text = ""
        for file_bytes, filename in files:
            chunks = extract_chunks_from_file(file_bytes, filename)
            combined_text += " ".join([c.text for c in chunks[:20]])
            logger.debug(f"Extracted chunks from {filename}")
        questions = suggest_questions(combined_text)
        logger.info(f"Session {session_id} ready | {len(files)} file(s) indexed")
        return questions
    except Exception as e:
        logger.error(f"File processing failed for session={session_id}: {e}")
        raise DocumentProcessingError(str(e))


def query_documents(
    session_id: str, question: str, history: list[ChatMessage]
) -> PDFQueryResponse:
    logger.info(f"Query | session={session_id} | question='{question[:60]}...'")

    if not session_exists(session_id):
        logger.warning(f"Session not found: {session_id}")
        raise SessionNotFoundError(session_id)

    store = load_vector_store(session_id)
    docs = store.similarity_search_with_score(question, k=5)
    logger.debug(f"Retrieved {len(docs)} chunks from FAISS")

    if not docs:
        return PDFQueryResponse(
            answer="No relevant content found in the uploaded documents.",
            citations=[],
        )

    scores = [score for _, score in docs]
    threshold = _adaptive_threshold(scores)
    logger.info(f"Adaptive threshold: {round(threshold, 3)} | best score: {round(min(scores), 3)}")

    context_parts = []
    citations: list[Citation] = []
    seen_pages = set()

    for doc, score in docs:
        logger.debug(f"Chunk score={round(score, 3)} | page={doc.metadata.get('page')} | accepted={score <= threshold}")
        if score <= threshold:
            context_parts.append(doc.page_content)
            page = doc.metadata.get("page", 0)
            if page not in seen_pages:
                seen_pages.add(page)
                citations.append(
                    Citation(page=page, chunk=doc.page_content[:200] + "...")
                )

    if not context_parts:
        logger.warning("All chunks filtered out — falling back to top 2")
        for doc, score in docs[:2]:
            context_parts.append(doc.page_content)
            page = doc.metadata.get("page", 0)
            if page not in seen_pages:
                seen_pages.add(page)
                citations.append(Citation(page=page, chunk=doc.page_content[:200] + "..."))

    logger.info(f"Answering with {len(context_parts)} chunks | {len(citations)} citations")
    context = "\n\n---\n\n".join(context_parts)
    answer = query_with_context(question, context, history)

    return PDFQueryResponse(answer=answer, citations=citations)