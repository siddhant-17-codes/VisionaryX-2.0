import io
import re
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter

from config.logger import setup_logger
from core.exceptions import DocumentProcessingError, UnsupportedFileTypeError

logger = setup_logger("visionaryx.chunker")


@dataclass
class Chunk:
    text: str
    page: int  # PDF page number; 0 for DOCX, which has no pages
    chunk_index: int
    section: str | None = None  # DOCX heading the chunk falls under


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
        return _split_pages([(page, None, text) for page, text in page_texts])
    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"PDF extraction failed: {e}") from e


def _safe_extract_text(page) -> str:
    """Extract text from a PDF page, trying three pypdf strategies in turn."""
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

    # Strategy 3 — collect text fragments through a visitor, dropping undecodable characters
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
    """DOCX has no pages, so chunks are labelled with the heading they fall under,
    and tables are read in document order, one row per line (F6)."""
    try:
        from docx import Document
        from docx.table import Table
        doc = Document(io.BytesIO(file_bytes))
        sections: list[tuple[str | None, list[str]]] = [(None, [])]
        for block in doc.iter_inner_content():
            if isinstance(block, Table):
                rows = (" | ".join(dict.fromkeys(c.text.strip() for c in row.cells if c.text.strip()))
                        for row in block.rows)
                text = "\n".join(row for row in rows if row)
                if text:
                    sections[-1][1].append(text)
                continue
            text = block.text.strip()
            if not text:
                continue
            style = block.style.name if block.style is not None else ""
            if style.startswith("Heading"):
                sections.append((text, [text]))
            else:
                sections[-1][1].append(text)
        if not any(body for _, body in sections):
            raise DocumentProcessingError("No readable text found in DOCX file.")
        logger.debug(f"DOCX extracted | {len(sections)} section(s)")
        return _split_pages([(0, title, "\n\n".join(body)) for title, body in sections if body])
    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"DOCX extraction failed: {e}") from e


def extract_chunks_from_file(file_bytes: bytes, filename: str) -> list[Chunk]:
    name = filename.lower()
    logger.info(f"Extracting chunks from: {filename}")
    if name.endswith(".pdf"):
        return extract_chunks_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_chunks_from_docx(file_bytes)
    else:
        raise UnsupportedFileTypeError(filename)


def _split_pages(parts: list[tuple[int, str | None, str]]) -> list[Chunk]:
    """Split (page, section, text) parts into chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks: list[Chunk] = []
    for page_num, section, text in parts:
        # Clean text before splitting
        cleaned = _clean_text(text)
        if not cleaned.strip():
            continue
        splits = splitter.split_text(cleaned)
        for idx, split in enumerate(splits):
            if split.strip():
                chunks.append(Chunk(text=split, page=page_num, chunk_index=idx, section=section))
    logger.debug(f"Split into {len(chunks)} chunks")
    return chunks


def _clean_text(text: str) -> str:
    """Clean and normalize extracted text, keeping line and paragraph breaks: the
    splitter cuts on them first, so chunks end at natural boundaries (F7)."""
    # Remove surrogate characters that cause encoding issues
    cleaned = text.encode("utf-8", errors="ignore").decode("utf-8")
    # Remove null bytes
    cleaned = cleaned.replace("\x00", " ")
    # Collapse runs of spaces and tabs, but not newlines
    cleaned = re.sub(r"[^\S\n]+", " ", cleaned)
    cleaned = re.sub(r" *\n *", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()