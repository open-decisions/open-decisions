import pathlib

import pytest

from open_decisions_documents.extract import extract, html_to_text, pdftotext_available
from open_decisions_documents.urls import bill_document_urls, measure_source_urls

FIXTURES = pathlib.Path(__file__).resolve().parents[3] / "fixtures" / "parlament"


def test_html_to_text_strips_markup_and_keeps_law_text():
    text = html_to_text((FIXTURES / "doc_XXVIII_A_73_gesetzestext.html").read_bytes())
    assert "<" not in text
    assert "Budgetsanierungsmaßnahmengesetz 2025" in text
    assert "Artikel 1" in text
    assert "Der Nationalrat hat beschlossen" in text


def test_extract_dispatches_on_content_type():
    text, pages, extractor = extract(b"<p>Hallo</p>", "text/html; charset=utf-8", "https://example.org/x.html")
    assert (text, pages, extractor) == ("Hallo", None, "html")


@pytest.mark.skipif(not pdftotext_available(), reason="pdftotext not installed")
def test_pdf_detection_by_magic_bytes_uses_pdftotext():
    with pytest.raises(Exception, match=r"pdftotext|Syntax|Command"):
        extract(b"%PDF-1.4 not really a pdf", None, "https://example.org/x")


def test_bill_document_urls_collects_all_kinds():
    bill = {
        "documents": {
            "law_text_html": "https://a/h",
            "law_text_pdf": "https://a/p",
            "explanations_pdf": "https://a/e",
            "impact_assessment_pdf": ["https://a/w1", "https://a/w2"],
        },
        "budget_office_analyses": [{"title": "x", "date": "2025-01-01", "url": "https://b", "pdf_url": "https://b/p"}],
    }
    assert bill_document_urls(bill) == ["https://a/h", "https://a/p", "https://a/e", "https://a/w1", "https://a/w2", "https://b/p"]


def test_measure_source_urls():
    assert measure_source_urls({"sources": [{"url": "https://s1"}, {"url": "https://s2"}]}) == ["https://s1", "https://s2"]
