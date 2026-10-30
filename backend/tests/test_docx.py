"""F6: DOCX is labelled by section (it has no pages), tables are read, .doc is refused."""
import io

import docx

from core.chunker import extract_chunks_from_docx
from tests.conftest import fixture_bytes

DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def handbook() -> bytes:
    doc = docx.Document()
    doc.add_paragraph("Welcome to the volunteer handbook.")
    doc.add_heading("Shifts", level=1)
    doc.add_paragraph("Shifts run Tuesday to Saturday.")
    table = doc.add_table(rows=2, cols=2)
    for row, values in zip(table.rows, [("Day", "Coordinator"), ("Tuesday", "Ines Okafor")], strict=True):
        for cell, value in zip(row.cells, values, strict=True):
            cell.text = value
    doc.add_heading("Lost property", level=2)
    doc.add_paragraph("Lost items are kept for 30 days.")
    out = io.BytesIO()
    doc.save(out)
    return out.getvalue()


def test_docx_chunks_carry_their_heading_and_no_fake_page():
    chunks = extract_chunks_from_docx(handbook())
    by_section = {c.section: c.text for c in chunks}
    assert set(by_section) == {None, "Shifts", "Lost property"}
    assert "Welcome" in by_section[None]
    assert "30 days" in by_section["Lost property"]
    assert all(c.page == 0 for c in chunks)


def test_docx_tables_are_read_row_by_row():
    shifts = next(c.text for c in extract_chunks_from_docx(handbook()) if c.section == "Shifts")
    assert "Day | Coordinator\nTuesday | Ines Okafor" in shifts


def test_docx_without_headings_is_one_unlabelled_section():
    chunks = extract_chunks_from_docx(fixture_bytes("harbor_lane_handbook.docx"))
    assert {c.section for c in chunks} == {None}
    assert "Tomas Reyes-Lindqvist" in " ".join(c.text for c in chunks)


def test_docx_citations_name_the_section(client, gemini):
    upload = client.post("/api/pdf/upload", files=[("files", ("handbook.docx", handbook(), DOCX))])
    query = client.post("/api/pdf/query", json={"session_id": upload.json()["session_id"], "question": "lost items"})
    citations = query.json()["citations"]
    assert citations
    assert all(c["source"] == "handbook.docx" and c["page"] == 0 for c in citations)
    assert {c["section"] for c in citations} <= {None, "Shifts", "Lost property"}
    keys = [(c["page"], c["section"]) for c in citations]
    assert len(keys) == len(set(keys))
