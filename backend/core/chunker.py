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
            text = page.extract_text() or ""
            if text.strip():
                page_texts.append((i + 1, text))
        logger.debug(f"PDF extracted | {len(page_texts)} pages with content")
        return _split_pages(page_texts)
    except Exception as e:
        raise DocumentProcessingError(f"PDF extraction failed: {e}")


def extract_chunks_from_docx(file_bytes: bytes) -> list[Chunk]:
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        logger.debug(f"DOCX extracted | {len(full_text)} characters")
        return _split_pages([(1, full_text)])
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
        splits = splitter.split_text(text)
        for idx, split in enumerate(splits):
            chunks.append(Chunk(text=split, page=page_num, chunk_index=idx))
    logger.debug(f"Split into {len(chunks)} chunks")
    return chunks