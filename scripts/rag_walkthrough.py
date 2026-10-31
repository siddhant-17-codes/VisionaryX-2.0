"""Walk through VisionaryX's RAG pipeline on local files and print every stage.

It runs the same code the backend runs for PDF Chat: extraction and chunking
(core/chunker.py), Gemini embeddings (core/embeddings.py), a LangChain FAISS index,
the adaptive threshold and citation builder (services/rag_service.py) and the
grounded answer (services/gemini_service.py). It mirrors rag_service.query_documents
step by step, but keeps the index in memory: nothing is written to Supabase, so the run
leaves no data behind.

Run it from backend/, in the backend's Python environment (it reads backend/.env):

    cd backend
    python ../scripts/rag_walkthrough.py ../examples/lumen_ridge_annual_report_2025.pdf \\
        ../examples/lumen_ridge_cold_storage_plan.docx \\
        -q "When will the new cold-storage building open, and what will it cost?"

Cost: one embedding request per 100 chunks, one for the question, and one generation
call for the answer (skip it with --no-answer). Only GOOGLE_API_KEY is needed.
"""

import argparse
import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
K = 5  # the same k as rag_service.query_documents


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(2)


def rule(title: str) -> None:
    print(f"\n=== {title} " + "=" * max(0, 70 - len(title)))


def load_backend():
    """Import the backend with its settings, or exit with a clear message."""
    os.chdir(BACKEND)  # Settings reads .env from the working directory
    sys.path.insert(0, str(BACKEND))
    # Settings for features this script does not use.
    os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", "")
    from pydantic import ValidationError

    from config.settings import get_settings

    try:
        settings = get_settings()
    except ValidationError:
        settings = None
    key = settings.google_api_key.strip() if settings else ""
    if not key or key.startswith("your_"):
        fail("GOOGLE_API_KEY is not set. Put it in backend/.env (see backend/.env.example) "
             "or export it, then run again. Get a key at https://aistudio.google.com/apikey")
    return settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path, help="PDF or DOCX files to index together")
    parser.add_argument("-q", "--question", required=True, help="the question to ask")
    parser.add_argument("--no-answer", action="store_true", help="stop after retrieval (no generation call)")
    parser.add_argument("--json", type=Path, help="also write every stage to this JSON file")
    parser.add_argument("--show", type=int, default=12, help="chunks to print in full (default 12)")
    args = parser.parse_args()

    files = [f.resolve() for f in args.files]
    for f in files:
        if not f.is_file():
            fail(f"{f} does not exist")
        if f.suffix.lower() not in (".pdf", ".docx"):
            fail(f"{f.name}: only .pdf and .docx are supported, as in the app")
    json_out = args.json.resolve() if args.json else None
    load_backend()

    import numpy as np
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document

    from core.chunker import extract_chunks_from_file
    from core.embeddings import EMBEDDING_MODEL, _batches, get_embeddings
    from models.schemas import PDFQueryResponse
    from services.rag_service import _adaptive_threshold, _cite

    report: dict = {"question": args.question, "files": [f.name for f in files]}

    # 1. Extraction and chunking, exactly as on upload.
    rule("1. Extract and chunk")
    docs = []
    for f in files:
        chunks = extract_chunks_from_file(f.read_bytes(), f.name)
        print(f"{f.name}: {len(chunks)} chunks")
        for c in chunks:
            docs.append(Document(page_content=c.text, metadata={
                "source": f.name, "page": c.page, "section": c.section, "chunk_index": c.chunk_index}))
    for i, d in enumerate(docs[: args.show]):
        m = d.metadata
        where = f"page {m['page']}" if m["page"] else f"section {m['section']!r}"
        preview = d.page_content[:90].replace("\n", " / ")
        print(f"  #{i:<2} {m['source']}, {where}, {len(d.page_content)} chars: {preview}...")
    if len(docs) > args.show:
        print(f"  ... {len(docs) - args.show} more")
    report["chunks"] = [{"id": i, "chars": len(d.page_content), **d.metadata} for i, d in enumerate(docs)]

    # 2. Embeddings: one request per batch of at most 100 chunks.
    rule("2. Embed the chunks")
    embeddings = get_embeddings()
    texts = [d.page_content for d in docs]
    batches = _batches(texts)
    vectors = np.array(embeddings.embed_documents(texts), dtype="float32")
    norms = np.linalg.norm(vectors, axis=1)
    print(f"model {EMBEDDING_MODEL}, task RETRIEVAL_DOCUMENT, {len(batches)} request(s)")
    print(f"matrix shape {vectors.shape} (chunks x dimensions)")
    print(f"vector lengths (L2 norm): min {norms.min():.4f}, max {norms.max():.4f}")
    report["embedding"] = {"model": EMBEDDING_MODEL, "requests": len(batches), "shape": list(vectors.shape),
                           "norm_min": float(norms.min()), "norm_max": float(norms.max())}

    # 3. The index, built the way FAISS.from_documents builds it in build_vector_store.
    rule("3. Build the FAISS index")
    store = FAISS.from_embeddings(list(zip(texts, vectors.tolist(), strict=True)), embeddings,
                                  metadatas=[d.metadata for d in docs])
    index = store.index
    print(f"{type(index).__name__}: {index.ntotal} vectors of {index.d} dimensions, "
          f"metric {'L2' if index.metric_type == 1 else index.metric_type}, normalize_L2={store._normalize_L2}")
    report["index"] = {"class": type(index).__name__, "ntotal": index.ntotal, "d": index.d}

    # 4. Retrieval: embed the question, take the K nearest, filter adaptively.
    rule("4. Retrieve")
    q = np.array(embeddings.embed_query(args.question), dtype="float32")
    print(f"question embedded with task RETRIEVAL_QUERY: shape {q.shape}, length {np.linalg.norm(q):.4f}")
    results = store.similarity_search_with_score_by_vector(q.tolist(), k=K)
    ids = {d.page_content: i for i, d in enumerate(docs)}
    top_id = ids[results[0][0].page_content]
    manual = float(((vectors[top_id] - q) ** 2).sum())
    print(f"check: FAISS score of the best chunk {results[0][1]:.6f}, "
          f"squared Euclidean distance computed by hand {manual:.6f}")
    scores = [float(s) for _, s in results]
    threshold = float(_adaptive_threshold(scores))
    print(f"best distance {min(scores):.4f} -> threshold min({min(scores):.4f} x 1.4, 2.0) = {threshold:.4f}")
    retrieved = []
    for rank, (doc, score) in enumerate(results, 1):
        m = doc.metadata
        kept = bool(score <= threshold)
        where = f"page {m['page']}" if m["page"] else f"section {m['section']!r}"
        print(f"  {rank}. {score:.4f} {'KEPT   ' if kept else 'dropped'} chunk #{ids[doc.page_content]} "
              f"{m['source']}, {where}")
        retrieved.append({"rank": rank, "distance": float(score), "kept": kept, "chunk": ids[doc.page_content],
                          "source": m["source"], "page": m["page"], "section": m["section"]})
    report["retrieval"] = {"k": K, "threshold": threshold, "results": retrieved}

    # 5. Context and citations, as query_documents builds them.
    rule("5. Context and citations")
    context_parts, citations, seen = [], [], set()
    for doc, score in results:
        if score <= threshold:
            context_parts.append(doc.page_content)
            _cite(doc, citations, seen)
    if not context_parts:
        print("every chunk was above the threshold: falling back to the top 2")
        for doc, _ in results[:2]:
            context_parts.append(doc.page_content)
            _cite(doc, citations, seen)
    context = "\n\n---\n\n".join(context_parts)
    print(f"{len(context_parts)} chunk(s) in the context, {len(context)} characters, separated by '---'")
    for n, c in enumerate(citations, 1):
        where = f"page {c.page}" if c.page else f"section {c.section!r}"
        print(f"  [{n}] {c.source}, {where}")
    report["context_chars"] = len(context)
    report["citations"] = [c.model_dump() for c in citations]

    # 6. The grounded answer.
    if not args.no_answer:
        rule("6. Answer")
        from services.gemini_service import query_with_context

        generated = query_with_context(args.question, context, history=[])
        response = PDFQueryResponse(answer=generated.text, citations=citations, model=generated.model)
        print(f"answered by {response.model}:\n{response.answer}")
        report["answer"] = {"model": response.model, "text": response.answer}

    if json_out:
        json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nwrote {json_out}")


if __name__ == "__main__":
    main()
