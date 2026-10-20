from collections.abc import Iterable
from typing import Any

from open_decisions_core import DATA
from open_decisions_core.records import load

DOCUMENT_KEYS = ("law_text_html", "law_text_pdf", "explanations_pdf", "comparison_pdf")


def bill_document_urls(bill: dict[str, Any]) -> list[str]:
    docs = bill.get("documents") or {}
    urls = [docs[k] for k in DOCUMENT_KEYS if docs.get(k)]
    urls += list(docs.get("impact_assessment_pdf") or [])
    urls += [a["pdf_url"] for a in bill.get("budget_office_analyses") or [] if a.get("pdf_url")]
    return urls


def measure_source_urls(measure: dict[str, Any]) -> list[str]:
    return [s["url"] for s in measure.get("sources", []) if s.get("url")]


def record_urls(kinds: Iterable[str] = ("bill", "measure")) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    folders = {"bill": "bills", "measure": "measures"}
    for kind in kinds:
        for path in sorted((DATA / folders[kind]).glob("*.yaml")):
            rec = load(path)
            urls = bill_document_urls(rec) if kind == "bill" else measure_source_urls(rec)
            for u in urls:
                out.setdefault(u, []).append(rec["id"])
    return out
