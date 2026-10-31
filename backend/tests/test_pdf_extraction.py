"""PDF text extraction: the example PDF still extracts page by page, and the three
pypdf strategies are tried in order."""
from pathlib import Path

from core import chunker

EXAMPLE = Path(__file__).resolve().parents[2] / "examples" / "lumen_ridge_annual_report_2025.pdf"


def test_example_pdf_extracts_every_page_with_its_number():
    chunks = chunker.extract_chunks_from_pdf(EXAMPLE.read_bytes())
    assert [c.page for c in chunks] == [1, 2, 3, 4]
    assert chunks[1].text.startswith("Harvest Results")
    assert "1,870 tonnes" in chunks[1].text
    assert "600,000 credits" in chunks[3].text


class FakePage:
    """Answers each extraction mode as configured, and records the order of calls."""

    def __init__(self, standard="", layout="", fragments=()):
        self.standard, self.layout, self.fragments = standard, layout, fragments
        self.calls = []

    def extract_text(self, extraction_mode="plain", visitor_text=None):
        if visitor_text is not None:
            self.calls.append("visitor")
            for fragment in self.fragments:
                visitor_text(fragment, None, None, None, None)
            return ""
        self.calls.append(extraction_mode)
        return self.layout if extraction_mode == "layout" else self.standard


def test_standard_extraction_is_used_when_it_works():
    page = FakePage(standard="Plain text")
    assert chunker._safe_extract_text(page) == "Plain text"
    assert page.calls == ["plain"]


def test_layout_mode_is_the_second_strategy():
    page = FakePage(layout="Layout text")
    assert chunker._safe_extract_text(page) == "Layout text"
    assert page.calls == ["plain", "layout"]


def test_visitor_is_the_last_strategy():
    page = FakePage(fragments=["Visitor", " ", "text"])
    assert chunker._safe_extract_text(page) == "Visitor text"
    assert page.calls == ["plain", "layout", "visitor"]


def test_a_page_with_no_text_gives_an_empty_string():
    page = FakePage()
    assert chunker._safe_extract_text(page) == ""
    assert page.calls == ["plain", "layout", "visitor"]
