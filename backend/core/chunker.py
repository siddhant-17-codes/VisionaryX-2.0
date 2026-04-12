import io
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.logger import setup_logger
from core.exceptions import DocumentProcessingError, UnsupportedFileTypeError

logger = setup_logger("visionaryx.chunker")


@dataclass
class Chunk:
    text: str
    page: int
    chunk_index: int


def extract_chunks_from_pdf(file_bytes: bytes) -> list[Chunk]:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        page_texts = []
        for i, page in enumerate(reader.pages):
            text = _safe_extract_text(page)
            if text.strip():
                page_texts.append((i + 1, text))
        if not page_texts:
            raise DocumentProcessingError("No readable text found in PDF. The file may be scanned or image-based.")
        logger.debug(f"PDF extracted | {len(page_texts)} pages with content")
        return _split_pages(page_texts)
    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"PDF extraction failed: {e}")


def _safe_extract_text(page) -> str:
    """Extract text from a PDF page with multiple fallback strategies."""
    # Strategy 1 — standard extraction
    try:
        text = page.extract_text()
        if text and text.strip():
            return text
    except Exception:
        pass

    # Strategy 2 — extract with layout mode
    try:
        text = page.extract_text(extraction_mode="layout")
        if text and text.strip():
            return text
    except Exception:
        pass

    # Strategy 3 — extract raw text parts individually
    try:
        parts = []
        if hasattr(page, "_objects"):
            for obj in page._objects:
                try:
                    if hasattr(obj, "get_text"):
                        t = obj.get_text()
                        if t:
                            parts.append(t)
                except Exception:
                    continue
        if parts:
            return " ".join(parts)
    except Exception:
        pass

    # Strategy 4 — extract with error ignore on encoding
    try:
        visitor_text = []
        def visitor(text, cm, tm, fontdict, fontSize):
            if text and text.strip():
                try:
                    cleaned = text.encode("utf-8", errors="ignore").decode("utf-8")
                    visitor_text.append(cleaned)
                except Exception:
                    pass
        page.extract_text(visitor_text=visitor)
        if visitor_text:
            return " ".join(visitor_text)
    except Exception:
        pass

    return ""


def extract_chunks_from_docx(file_bytes: bytes) -> list[Chunk]:
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        full_text = "\n".join([
            p.text for p in doc.paragraphs
            if p.text and p.text.strip()
        ])
        if not full_text.strip():
            raise DocumentProcessingError("No readable text found in DOCX file.")
        logger.debug(f"DOCX extracted | {len(full_text)} characters")
        return _split_pages([(1, full_text)])
    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"DOCX extraction failed: {e}")


def extract_chunks_from_file(file_bytes: bytes, filename: str) -> list[Chunk]:
    name = filename.lower()
    logger.info(f"Extracting chunks from: {filename}")
    if name.endswith(".pdf"):
        return extract_chunks_from_pdf(file_bytes)
    elif name.endswith(".docx") or name.endswith(".doc"):
        return extract_chunks_from_docx(file_bytes)
    else:
        raise UnsupportedFileTypeError(filename)


def _split_pages(page_texts: list[tuple[int, str]]) -> list[Chunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[Chunk] = []
    for page_num, text in page_texts:
        # Clean text before splitting
        cleaned = _clean_text(text)
        if not cleaned.strip():
            continue
        splits = splitter.split_text(cleaned)
        for idx, split in enumerate(splits):
            if split.strip():
                chunks.append(Chunk(text=split, page=page_num, chunk_index=idx))
    logger.debug(f"Split into {len(chunks)} chunks")
    return chunks


def _clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove surrogate characters that cause encoding issues
    cleaned = text.encode("utf-8", errors="ignore").decode("utf-8")
    # Remove null bytes
    cleaned = cleaned.replace("\x00", " ")
    # Normalize whitespace
    import re
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()