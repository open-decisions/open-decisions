import html
import re
from datetime import date, datetime
from typing import Any

from open_decisions_ingest_at import BASE_URL, BILL_TYPES, JURISDICTION, LANG, PARTY_WIKIDATA

PHASES = {
    "Einlangen NR": ("introduced", "Nationalrat"),
    "Einbringung NR": ("introduced", "Nationalrat"),
    "Ausschussberatungen NR": ("committee", "Nationalrat"),
    "Plenarberatungen NR": ("plenary", "Nationalrat"),
    "Einlangen BR": ("second_chamber_introduced", "Bundesrat"),
    "Ausschussberatungen BR": ("second_chamber_committee", "Bundesrat"),
    "Plenarberatungen BR": ("second_chamber_plenary", "Bundesrat"),
}
DOCUMENT_KINDS = [
    ("Vorblatt und WFA", "impact_assessment_pdf"),
    ("Gesetzestext", "law_text"),
    ("Erläuterungen", "explanations_pdf"),
    ("Textgegenüberstellung", "comparison_pdf"),
    ("Initiativantrag", "law_text"),
]
TAG = re.compile(r"<[^>]+>")
HREF = re.compile(r'href="([^"]+)"')
BGBL = re.compile(r"Bundesgesetzblatt\s+(I{1,3})\s+Nr\.\s*(\d+)/(\d{4})")


def strip_html(text: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", text or ""))).strip()


def first_href(text: str | None) -> str | None:
    m = HREF.search(text or "")
    if not m:
        return None
    href = html.unescape(m.group(1))
    return href if href.startswith("http") else BASE_URL + href


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%d.%m.%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value[: len("2025-05-13T00:00:00")] if "T" in value else value, fmt).date()
        except ValueError:
            continue
    return None


def eli_from_bgbl(title: str | None) -> str | None:
    m = BGBL.search(title or "")
    if not m:
        return None
    part, number, year = m.groups()
    return f"https://www.ris.bka.gv.at/eli/bgbl/{part}/{year}/{number}"


def bubbles(block: dict[str, Any] | None) -> list[str]:
    return [b["label"] for b in ((block or {}).get("data") or {}).get("bubbles", []) if b.get("label")]


def documents(content: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for group in content.get("documents", []):
        title = group.get("title", "")
        kind = next((k for prefix, k in DOCUMENT_KINDS if title.startswith(prefix)), None)
        if kind is None:
            continue
        links = {d["type"]: BASE_URL + d["link"] for d in group.get("documents", []) if d.get("link")}
        if kind == "impact_assessment_pdf":
            out.setdefault(kind, []).append(links.get("PDF") or next(iter(links.values())))
        elif kind == "law_text":
            if "HTML" in links:
                out.setdefault("law_text_html", links["HTML"])
            if "PDF" in links:
                out.setdefault("law_text_pdf", links["PDF"])
        else:
            out.setdefault(kind, links.get("PDF") or next(iter(links.values())))
    return out


def phases(content: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for block in content.get("phase", []):
        mapped = PHASES.get(block.get("name", ""))
        if mapped is None:
            continue
        phase, chamber = mapped
        for stage in block.get("stages", []):
            d = parse_date(stage.get("date"))
            text = strip_html(stage.get("text"))
            if d is None or not text:
                continue
            out.append({"phase": phase, "chamber": chamber, "date": d, "text": text, "url": first_href(stage.get("text"))})
    return out


def stage_of(content: dict[str, Any], has_vote: bool, phase_names: set[str] | None = None) -> str:
    status = content.get("status") or {}
    desc = strip_html(status.get("description"))
    if status.get("bgbllinks"):
        return "published"
    if "Beschlossen im Bundesrat" in desc:
        return "passed_second_chamber"
    if "Beschlossen im Nationalrat" in desc or has_vote:
        return "passed_first_chamber"
    if "committee" in (phase_names or set()) or str(status.get("number")) in ("3", "4"):
        return "committee"
    return "introduced"


def vote_date(ph: list[dict[str, Any]]) -> date | None:
    plenary = [p for p in ph if p["phase"] == "plenary"]
    for marker in ("in dritter Lesung", "Beschluss im Nationalrat"):
        hit = next((p for p in plenary if marker in p["text"]), None)
        if hit:
            return hit["date"]
    return max((p["date"] for p in plenary), default=None)


def vote(content: dict[str, Any], when: date | None) -> dict[str, Any] | None:
    v = content.get("vote") or {}
    result = v.get("result") or []
    if not result or when is None:
        return None
    return {
        "date": when,
        "result": [
            {
                "party": r["text"],
                "wikidata": PARTY_WIKIDATA.get(r["text"]),
                "seats": int(r.get("fraction") or 0),
                "in_favor": bool(r.get("infavor")),
            }
            for r in result
        ],
        "note": strip_html(v.get("text")) or None,
    }


def bill_from_item(payload: dict[str, Any], fetched_at: datetime) -> dict[str, Any]:
    c = payload["content"]
    if c.get("doktyp") not in BILL_TYPES:
        raise ValueError(f"not a bill: doktyp {c.get('doktyp')!r}")
    gp, ityp, inr = c["gp_code"], c["ityp"], str(c["inr"])
    ph = phases(c)
    v = vote(c, vote_date(ph))
    status = c.get("status") or {}
    bgbl = next((b for b in status.get("bgbllinks", []) if "Bundesgesetzblatt" in (b.get("title") or "")), None)
    return {
        "id": f"{JURISDICTION}/{gp}/{ityp}/{inr}",
        "jurisdiction": JURISDICTION,
        "gp": gp,
        "ityp": ityp,
        "inr": inr,
        "type": BILL_TYPES[c["doktyp"]],
        "title": c["title"],
        "citation": c.get("zitation"),
        "parliament_url": f"{BASE_URL}/gegenstand/{gp}/{ityp}/{inr}",
        "introduced": parse_date(c.get("einlangen")),
        "introduced_by": [n["name"] + (f" ({n['ltext']})" if n.get("ltext") else "") for n in c.get("names", []) if n.get("name")],
        "stage": stage_of(c, v is not None, {p["phase"] for p in ph}),
        "source_status": str(status.get("number")) if status.get("number") is not None else None,
        "gazette": (bgbl or {}).get("title"),
        "gazette_url": (bgbl or {}).get("link"),
        "eli": eli_from_bgbl((bgbl or {}).get("title")),
        "eurovoc": bubbles(c.get("eurovoc")),
        "topics": bubbles(c.get("topics")),
        "keywords": bubbles(c.get("headwords")),
        "documents": documents(c),
        "pre_parliamentary": [
            {"citation": p["zitation"], "title": p["betreff"], "url": BASE_URL + p["url"]} for p in c.get("preconst", []) if p.get("url")
        ],
        "vote": v,
        "phases": ph,
        "source_updated": parse_date(c.get("update")),
        "fetched_at": fetched_at,
    }


def record_from_bill(bill: dict[str, Any], curated: dict[str, Any] | None = None) -> dict[str, Any]:
    curated = curated or {}
    iso = lambda d: d.isoformat() if hasattr(d, "isoformat") else d  # noqa: E731
    rec: dict[str, Any] = {
        "kind": "bill",
        "jurisdiction": bill["jurisdiction"],
        "lang": LANG,
        "id": bill["id"],
        "type": bill["type"],
        "title": bill["title"],
        "citation": bill["citation"],
        "parliament_url": bill["parliament_url"],
        "introduced": iso(bill["introduced"]),
        "introduced_by": bill["introduced_by"],
        "identifiers": {
            k: v
            for k, v in {
                "eli": bill["eli"],
                "eurovoc": bill["eurovoc"],
                "topics": bill["topics"],
                "keywords": bill["keywords"],
            }.items()
            if v
        },
        "status": {
            k: v
            for k, v in {
                "stage": bill["stage"],
                "source_status": bill["source_status"],
                "gazette": bill["gazette"],
                "gazette_url": bill["gazette_url"],
            }.items()
            if v is not None
        },
        "pre_parliamentary": bill["pre_parliamentary"],
        "phases": [{k: v for k, v in {**p, "date": iso(p["date"])}.items() if v is not None} for p in bill["phases"]],
        "vote": None,
        "documents": bill["documents"],
        "budget_office_analyses": curated.get("budget_office_analyses", []),
        "measures": curated.get("measures", []),
        "sources": [
            {
                "id": "parl-detail",
                "role": "law_text",
                "institution": "Parlament Österreich",
                "title": f"Verhandlungsgegenstand {bill['citation'] or bill['id']}, Detail-JSON",
                "url": bill["parliament_url"] + "?json=TRUE",
                "retrieved": iso(bill["fetched_at"].date()),
                "archive": None,
            }
        ],
        "retrieved": iso(bill["fetched_at"].date()),
    }
    if bill["vote"]:
        v = bill["vote"]
        rec["vote"] = {
            "date": iso(v["date"]),
            "result": [{k: x for k, x in r.items() if x is not None} for r in v["result"]],
            **({"note": v["note"]} if v.get("note") else {}),
        }
    eu = bill.get("eu_relation")
    if eu:
        curated_eu = curated.get("eu_relation") or {}
        if curated_eu.get("checked"):
            rec["eu_relation"] = curated_eu
        else:
            rec["eu_relation"] = {**eu, "method": "text_extraction", "checked": False}
    if not rec["identifiers"]:
        del rec["identifiers"]
    if not rec["pre_parliamentary"]:
        del rec["pre_parliamentary"]
    if not rec["budget_office_analyses"]:
        del rec["budget_office_analyses"]
    if rec["citation"] is None:
        del rec["citation"]
    if rec["introduced"] is None:
        rec["introduced"] = iso(bill["fetched_at"].date())
    return rec
