import pytest

from tests.conftest import OWNER, OWNER_HASH, STRANGER, fixture_bytes

PDF = "application/pdf"
DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_upload_indexes_and_suggests_questions(uploaded_pdf, supabase):
    assert uploaded_pdf.files_processed == 1
    assert uploaded_pdf.questions == ["What is A?", "What is B?", "What is C?"]
    stored = supabase.db["faiss_indexes"]
    assert [row["session_id"] for row in stored] == [uploaded_pdf.session_id]


def test_upload_links_index_to_chat_session(client, uploaded_pdf):
    session = client.get(f"/api/sessions/{uploaded_pdf.chat_id}").json()
    assert session["session_id"] == uploaded_pdf.session_id
    assert session["documents"] == ["lumen_ridge_report.pdf"]
    assert session["title"] == "lumen_ridge_report.pdf"


def test_query_answers_with_page_citations(client, uploaded_pdf, gemini):
    res = client.post("/api/pdf/query", json={
        "session_id": uploaded_pdf.session_id,
        "question": "What was the total apple harvest in 2025?",
        "chat_session_id": uploaded_pdf.chat_id,
    })
    assert res.status_code == 200
    body = res.json()
    assert body["answer"] == gemini.answer
    assert body["citations"], "expected at least one citation"
    assert all(1 <= c["page"] <= 4 for c in body["citations"])
    # Retrieved document text reaches the model as context, with the rules as a system instruction.
    assert "Lumen" in gemini.prompts[-1] or "tonnes" in gemini.prompts[-1] or "credits" in gemini.prompts[-1]
    assert "Answer ONLY from the provided context" in gemini.configs[-1].system_instruction


def test_query_persists_to_chat_session(client, uploaded_pdf):
    client.post("/api/pdf/query", json={
        "session_id": uploaded_pdf.session_id, "question": "Who is the treasurer?",
        "chat_session_id": uploaded_pdf.chat_id,
    })
    messages = client.get(f"/api/sessions/{uploaded_pdf.chat_id}").json()["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant"]


def test_multi_document_upload(client):
    res = client.post("/api/pdf/upload", files=[
        ("files", ("lumen_ridge_report.pdf", fixture_bytes("lumen_ridge_report.pdf"), PDF)),
        ("files", ("harbor_lane_handbook.docx", fixture_bytes("harbor_lane_handbook.docx"), DOCX)),
    ])
    assert res.status_code == 200
    assert res.json()["files_processed"] == 2


def test_index_survives_restart(client, uploaded_pdf):
    """The index lives in Supabase, so a fresh process can load and query it."""
    from core.vector_store import load_vector_store

    store = load_vector_store(uploaded_pdf.session_id, OWNER_HASH)
    assert store.similarity_search("harvest", k=1)


def test_query_unknown_index_returns_404(client):
    res = client.post("/api/pdf/query", json={"session_id": "nope", "question": "hi"})
    assert res.status_code == 404
    assert res.json()["type"] == "SessionNotFoundError"


def test_upload_rejects_unsupported_type(client):
    res = client.post("/api/pdf/upload", files=[("files", ("notes.txt", b"hello", "text/plain"))])
    assert res.status_code == 400


def test_upload_corrupt_pdf_returns_422(client):
    res = client.post("/api/pdf/upload", files=[("files", ("bad.pdf", fixture_bytes("not_a_pdf.pdf"), PDF))])
    assert res.status_code == 422
    assert res.json()["type"] == "DocumentProcessingError"


def test_upload_scanned_pdf_explains_no_text(client):
    res = client.post("/api/pdf/upload", files=[("files", ("scan.pdf", fixture_bytes("scanned_page.pdf"), PDF))])
    assert res.status_code == 422
    assert "scanned" in res.json()["error"]


def test_deleting_session_deletes_its_index(client, uploaded_pdf, supabase):
    client.delete(f"/api/sessions/{uploaded_pdf.chat_id}")
    assert supabase.db["faiss_indexes"] == []


def test_index_and_session_store_only_the_hashed_owner(uploaded_pdf, supabase):
    assert [row["owner_id"] for row in supabase.db["faiss_indexes"]] == [OWNER_HASH]
    assert [row["owner_id"] for row in supabase.db["sessions"]] == [OWNER_HASH]
    assert OWNER not in repr(supabase.db)  # the raw X-Client-Id never reaches the database


def test_stranger_cannot_query_someone_elses_index(client, uploaded_pdf, gemini):
    calls_before = len(gemini.prompts)
    res = client.post("/api/pdf/query", headers=STRANGER,
                      json={"session_id": uploaded_pdf.session_id, "question": "harvest"})
    assert res.status_code == 404
    assert len(gemini.prompts) == calls_before


def test_stranger_cannot_upload_into_someone_elses_session(client, uploaded_pdf):
    res = client.post(
        "/api/pdf/upload", headers=STRANGER,
        files=[("files", ("lumen_ridge_report.pdf", fixture_bytes("lumen_ridge_report.pdf"), PDF))],
        data={"chat_session_id": uploaded_pdf.chat_id},
    )
    assert res.status_code == 404
    assert client.get(f"/api/sessions/{uploaded_pdf.chat_id}").json()["session_id"] == uploaded_pdf.session_id


def test_citations_name_the_source_file(client, uploaded_pdf):
    res = client.post("/api/pdf/query", json={"session_id": uploaded_pdf.session_id, "question": "harvest"})
    assert res.json()["citations"][0]["source"] == "lumen_ridge_report.pdf"


def test_citations_from_several_files_keep_their_own_source(client):
    files = [
        ("files", ("lumen_ridge_report.pdf", fixture_bytes("lumen_ridge_report.pdf"), PDF)),
        ("files", ("harbor_lane_handbook.docx", fixture_bytes("harbor_lane_handbook.docx"), DOCX)),
    ]
    session_id = client.post("/api/pdf/upload", files=files).json()["session_id"]
    from core.vector_store import load_vector_store
    store = load_vector_store(session_id, OWNER_HASH)
    sources = {doc.metadata["source"] for doc in store.docstore._dict.values()}
    assert sources == {"lumen_ridge_report.pdf", "harbor_lane_handbook.docx"}

    res = client.post("/api/pdf/query", json={"session_id": session_id, "question": "harvest"})
    citations = res.json()["citations"]
    keys = [(c["source"], c["page"]) for c in citations]
    assert keys and len(keys) == len(set(keys))
    assert {c["source"] for c in citations} <= sources


def test_same_page_number_in_two_files_gives_two_citations():
    from langchain.schema import Document

    from services.rag_service import _cite
    citations, seen = [], set()
    for source in ("a.pdf", "b.pdf", "a.pdf"):
        _cite(Document(page_content="text", metadata={"source": source, "page": 1}), citations, seen)
    assert [(c.source, c.page) for c in citations] == [("a.pdf", 1), ("b.pdf", 1)]


def test_index_built_before_sources_were_stored_still_cites_pages():
    from langchain.schema import Document

    from services.rag_service import _cite
    citations = []
    _cite(Document(page_content="text", metadata={"page": 3}), citations, set())
    assert citations[0].source is None and citations[0].page == 3


@pytest.mark.xfail(strict=True, reason="F6: fixed in fix/backend-robustness")
def test_upload_rejects_legacy_doc(client):
    res = client.post("/api/pdf/upload", files=[("files", ("old.doc", b"\xd0\xcf\x11\xe0", "application/msword"))])
    assert res.status_code == 400
