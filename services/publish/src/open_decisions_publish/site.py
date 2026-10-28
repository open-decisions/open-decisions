import json
import pathlib
import re
from datetime import date
from typing import Any

from open_decisions_core import DATA
from open_decisions_core.records import load
from open_decisions_core.style import FORBIDDEN
from open_decisions_publish.cards import card_view
from open_decisions_publish.format import STATES, german_date, german_number

STEPS = {"pre_parliamentary": 0, "introduced": 1, "committee": 2, "passed_first_chamber": 3, "passed_second_chamber": 4, "published": 5}
STEP_LABELS = {
    "pre_parliamentary": "in Begutachtung",
    "introduced": "eingebracht, noch keinem Ausschuss zugewiesen",
    "committee": "im Ausschuss",
    "passed_first_chamber": "Nationalrat beschlossen, Bundesrat ausständig",
    "passed_second_chamber": "Bundesrat durch, Kundmachung ausständig",
    "published": "im Bundesgesetzblatt, gilt",
}
STAGE_FILTERS = [
    ("introduced", "Eingebracht"),
    ("committee", "Im Ausschuss"),
    ("passed_first_chamber", "Nationalrat beschlossen"),
    ("passed_second_chamber", "Bundesrat durch"),
    ("published", "Gilt"),
]
ROLE_LABELS = {
    "law_text": "Gesetz",
    "impact_assessment": "Folgenabschätzung",
    "parliamentary_budget_office": "Budgetdienst",
    "statistics": "Statistik",
    "study": "Studie",
    "government_communication": "Regierung, nur für das Zitat",
}
TOPIC_LABELS = {
    "taxes": "Steuern",
    "transfers": "Transfers",
    "pensions": "Pensionen",
    "fees": "Gebühren",
    "minimum_wage": "Mindestlohn",
    "indexation": "Inflationsanpassung",
    "other": "Sonstiges",
}
EU_LABELS = {
    "transposes_directive": "setzt eine EU-Vorgabe um",
    "implements_regulation": "ergänzt eine EU-Verordnung, die direkt gilt",
    "eu_scope": "im Rahmen des EU-Rechts, aber nicht von der EU verlangt",
    "national": "rein österreichische Regelung",
}
EU_FILTERS = [
    ("eu_law", "Setzt EU-Vorgaben um"),
    ("eu_scope", "Im Rahmen des EU-Rechts"),
    ("national", "Rein österreichisch"),
    ("not_stated", "Keine Angabe"),
]
TYPE_FILTERS = [("government_bill", "Regierungsvorlagen", "Regierungsvorlage"), ("members_bill", "Initiativanträge", "Initiativantrag")]


def household_description(h: dict[str, Any]) -> str:
    parts = [h["label"]]
    employment = h.get("employment", "")
    if "€" in employment:
        parts.append(employment[:1].upper() + employment[1:])
    else:
        incomes = [german_number(x) + " €" for x in h["gross_income_month"] if x]
        if incomes:
            text = " und ".join(incomes) + " brutto im Monat"
            if len(incomes) < len(h["gross_income_month"]):
                text += ", zweite Person ohne Einkommen"
            parts.append(text)
    if h.get("other_income"):
        parts.append("Dazu " + h["other_income"])
    parts.append(f"{h['housing']}, {h['region']}")
    return ". ".join(parts) + "."


def households_view(country: str) -> list[dict[str, Any]]:
    data = load(DATA / "households" / f"{country}.yaml")
    return [
        {"id": h["id"], "short": h.get("short_label", h["label"]), "label": h["label"], "description": household_description(h)}
        for h in data["households"]
    ]


def path_view(bill: dict[str, Any]) -> list[dict[str, str]]:
    phases = bill.get("phases", [])

    def first(kind):
        return next((p for p in phases if p["phase"] == kind), None)

    def last(kind):
        return next((p for p in reversed(phases) if p["phase"] == kind), None)

    out = []
    if p := first("introduced"):
        kind = "Regierungsvorlage" if bill["type"] == "government_bill" else "Initiativantrag"
        out.append({"label": "Eingebracht", "detail": f"{german_date(p['date'])}, {kind}"})
    if p := first("committee"):
        out.append({"label": "Ausschuss", "detail": f"ab {german_date(p['date'])}"})
    vote, plenary = bill.get("vote"), last("plenary")
    if vote or plenary:
        chamber = (plenary or {}).get("chamber", "Nationalrat")
        when = vote["date"] if vote else plenary["date"] if plenary else None
        if when:
            out.append({"label": f"{chamber} beschließt", "detail": german_date(when)})
    if p := last("second_chamber_plenary"):
        out.append({"label": p.get("chamber", "Zweite Kammer"), "detail": german_date(p["date"])})
    if bill["status"].get("gazette"):
        out.append({"label": "Kundgemacht", "detail": bill["status"]["gazette"]})
    return out


def vote_view(bill: dict[str, Any]) -> dict[str, Any] | None:
    vote = bill.get("vote")
    if not vote:
        return None
    yes = [r for r in vote["result"] if r["in_favor"]]
    no = [r for r in vote["result"] if not r["in_favor"]]
    seats_yes, seats_no = sum(r["seats"] for r in yes), sum(r["seats"] for r in no)
    total = seats_yes + seats_no or 1
    return {
        "date": german_date(vote["date"]),
        "session": vote.get("session"),
        "yes": {"seats": seats_yes, "parties": [f"{r['party']} {r['seats']}" for r in yes]},
        "no": {"seats": seats_no, "parties": [f"{r['party']} {r['seats']}" for r in no]},
        "share_yes": round(seats_yes / total * 100, 1),
    }


def eu_view(bill: dict[str, Any]) -> dict[str, Any]:
    rel = bill.get("eu_relation") or {"kind": "not_stated", "kinds": [], "goes_beyond": False, "acts": [], "checked": False}
    kind = rel["kind"]
    group = "eu_law" if kind in ("transposes_directive", "implements_regulation") else kind
    label = EU_LABELS.get(kind)
    partial = group == "eu_law" and any(k in ("national", "eu_scope") for k in rel.get("kinds", []))
    if label and partial:
        label = "teils: " + label
    return {
        "group": group,
        "label": label,
        "goes_beyond": rel.get("goes_beyond", False),
        "goes_beyond_text": "geht laut Folgenabschätzung über die EU-Vorgaben hinaus" if rel.get("goes_beyond") else None,
        "acts": [{"label": a["label"], "url": a["eurlex_url"], "role": a["role"]} for a in rel.get("acts", [])],
        "checked": rel.get("checked", False),
    }


AREAS = {
    "AT": [
        ("arbeit", "Arbeit", ["Arbeit"]),
        ("soziales", "Soziales und Pensionen", ["Soziales"]),
        ("familie", "Familie und Gleichstellung", ["Familie und Generationen", "Frauen und Gleichbehandlung"]),
        ("gesundheit", "Gesundheit", ["Gesundheit und Ernährung"]),
        ("steuern", "Steuern und Budget", ["Budget und Finanzen"]),
        ("wirtschaft", "Wirtschaft", ["Wirtschaft", "Innovation, Technologie und Forschung", "Land- und Forstwirtschaft"]),
        ("energie", "Energie und Umwelt", ["Klima, Umwelt und Energie"]),
        ("verkehr", "Verkehr", ["Verkehr und Infrastruktur"]),
        ("bildung", "Bildung und Kultur", ["Bildung", "Kultur"]),
        ("recht", "Sicherheit und Recht", ["Inneres und Recht", "Landesverteidigung"]),
        ("demokratie", "Demokratie und Medien", ["Parlament und Demokratie", "Information und Medien"]),
        ("europa", "EU und Außenpolitik", ["Europäische Union", "Außenpolitik"]),
    ]
}
COMPOUND_FORBIDDEN = re.compile(r"(reform|paket|entlastung|belastung|geschenk|kürzung|grünes licht)", re.I)
PRESS_PREFIX = re.compile(r"^[A-ZÄÖÜ][\wäöüß-]{2,40}(?: [A-ZÄÖÜ][\wäöüß-]+)?: ")
PRESS_PHRASES = [
    (re.compile(r"^Grünes Licht für (die |den |das )?", re.I), ""),
    (re.compile(r"\s+(im Ausschuss )?beschlossen$"), ""),
]
RECENT_DAYS = 30
NEW_DAYS = 21


def areas_of(bill: dict[str, Any], country: str) -> list[dict[str, str]]:
    topics = set((bill.get("identifiers") or {}).get("topics", []))
    return [{"id": k, "label": label} for k, label, ts in AREAS.get(country, []) if topics & set(ts)]


def clean_press(title: str) -> str:
    text = PRESS_PREFIX.sub("", title.strip())
    for rx, repl in PRESS_PHRASES:
        text = rx.sub(repl, text).strip()
    return text[:1].upper() + text[1:] if text else text


def headline(bill: dict[str, Any]) -> dict[str, Any]:
    for p in reversed(bill.get("press", [])):
        if not p.get("heading"):
            continue
        text = clean_press(p["heading"])
        if 12 <= len(text) <= 160 and not FORBIDDEN.search(text) and not COMPOUND_FORBIDDEN.search(text):
            return {"text": text, "source": "Parlamentskorrespondenz", "url": p["url"]}
    for item in bill.get("summary", []):
        if 12 <= len(item) <= 160 and not FORBIDDEN.search(item) and not COMPOUND_FORBIDDEN.search(item):
            return {"text": item, "source": "Kurzinformation der Parlamentsdirektion", "url": bill["parliament_url"]}
    return {"text": bill["title"], "source": None, "url": None}


def duration(since: str, today: str) -> str:
    days = (date.fromisoformat(today) - date.fromisoformat(since)).days
    if days <= 1:
        return "seit gestern" if days == 1 else "seit heute"
    if days < 14:
        return f"seit {days} Tagen"
    if days < 63:
        return f"seit {days // 7} Wochen"
    months = days // 30
    return "seit einem Monat" if months == 1 else f"seit {months} Monaten"


def stage_text(bill: dict[str, Any], today: str) -> str:
    stage = bill["status"]["stage"]
    phases = bill.get("phases", [])
    first_committee = next((p["date"] for p in phases if p["phase"] == "committee"), None)
    vote = (bill.get("vote") or {}).get("date")
    br = next((p["date"] for p in reversed(phases) if p["phase"] == "second_chamber_plenary" and p["date"] <= today), None)
    if stage == "introduced":
        return f"eingebracht {duration(bill['introduced'], today)}, noch keinem Ausschuss zugewiesen"
    if stage == "committee":
        return f"wird {duration(first_committee or bill['introduced'], today)} im Ausschuss beraten"
    if stage == "passed_first_chamber":
        return f"vom Nationalrat am {german_date(vote)} beschlossen, der Bundesrat ist noch dran" if vote else STEP_LABELS[stage]
    if stage == "passed_second_chamber":
        return f"vom Bundesrat am {german_date(br)} bestätigt, wird demnächst kundgemacht" if br else STEP_LABELS[stage]
    if stage == "published":
        decided = f"im Nationalrat am {german_date(vote)} beschlossen" if vote else "beschlossen"
        gazette = bill["status"].get("gazette")
        return f"gilt: {decided}, kundgemacht im {gazette}" if gazette else f"gilt: {decided}"
    return STEP_LABELS[stage]


def happening(bill: dict[str, Any], today: str) -> list[str]:
    t = date.fromisoformat(today)
    tags = []
    upcoming = [p for p in bill.get("phases", []) if p["date"] > today]
    if upcoming:
        tags.append("upcoming")
    vote = (bill.get("vote") or {}).get("date")
    br = [p["date"] for p in bill.get("phases", []) if p["phase"] == "second_chamber_plenary" and p["date"] <= today]
    last_decision = max([d for d in [vote, *br] if d], default=None)
    if last_decision and (t - date.fromisoformat(last_decision)).days <= RECENT_DAYS:
        tags.append("decided")
    if (t - date.fromisoformat(bill["introduced"])).days <= NEW_DAYS:
        tags.append("new")
    return tags


def next_date(bill: dict[str, Any], today: str) -> dict[str, str] | None:
    upcoming = sorted((p for p in bill.get("phases", []) if p["date"] > today), key=lambda p: p["date"])
    if not upcoming:
        return None
    p = upcoming[0]
    chamber = p.get("chamber")
    genitive = {"Nationalrat": "des Nationalrats", "Bundesrat": "des Bundesrats"}.get(chamber or "", "")
    what = "Ausschuss" if "committee" in p["phase"] else "Sitzung"
    return {"date": p["date"], "text": f"{what} {genitive} am {german_date(p['date'])}".replace("  ", " ")}


def bill_row(bill: dict[str, Any], today: str, country: str = "AT") -> dict[str, Any]:
    stage = bill["status"]["stage"]
    kind = next(t[2] for t in TYPE_FILTERS if t[0] == bill["type"])
    head = headline(bill)
    return {
        "headline": head["text"],
        "headline_source": head["source"],
        "headline_url": head["url"],
        "areas": areas_of(bill, country),
        "stage_text": stage_text(bill, today),
        "happening": happening(bill, today),
        "next": next_date(bill, today),
        "id": bill["id"],
        "slug": bill["id"].replace("/", "-"),
        "citation": bill.get("citation") or bill["id"],
        "title": bill["title"],
        "type": bill["type"],
        "kind": kind,
        "introduced": bill["introduced"],
        "introduced_text": german_date(bill["introduced"]),
        "stage": stage,
        "step": STEPS[stage],
        "step_label": STEP_LABELS[stage],
        "measures": bill.get("measures", []),
        "parliament_url": bill["parliament_url"],
        "eu": eu_view(bill),
    }


def bill_page(bill: dict[str, Any], today: str, country: str = "AT") -> dict[str, Any]:
    row = bill_row(bill, today, country)
    rel = bill.get("eu_relation") or {}
    docs = bill.get("documents", {})
    doc_links = []
    for key, label in (
        ("law_text_html", "Gesetzestext"),
        ("explanations_pdf", "Erläuterungen"),
        ("comparison_pdf", "Textgegenüberstellung alt und neu"),
    ):
        if docs.get(key):
            doc_links.append({"label": label, "url": docs[key]})
    for i, url in enumerate(docs.get("impact_assessment_pdf", []), 1):
        suffix = f", Teil {i}" if len(docs.get("impact_assessment_pdf", [])) > 1 else ""
        doc_links.append({"label": f"Folgenabschätzung der Regierung{suffix}", "url": url})
    return {
        **row,
        "summary": bill.get("summary", []),
        "press": [
            {"title": p.get("heading") or p["title"], "date": german_date(p["date"]), "url": p["url"]}
            for p in reversed(bill.get("press", []))
        ],
        "path": path_view(bill),
        "vote": vote_view(bill),
        "eu_statements": [
            {"text": s["text"], "url": s["source"], "page": s.get("page")}
            for s in rel.get("statements", [])
            if s["kind"] != "eu_scope" or s["text"]
        ],
        "documents": doc_links,
        "introduced_by": bill.get("introduced_by", []),
    }


def site_data(country: str = "AT") -> dict[str, Any]:
    bills = [load(p) for p in sorted((DATA / "bills").glob(f"{country}-*.yaml"))]
    by_id = {b["id"]: b for b in bills}
    cards = []
    for path in sorted((DATA / "measures").glob(f"{country.lower()}-*.yaml")):
        measure = load(path)
        card = card_view(measure)
        bill = by_id[measure["bill"]]
        state = measure["status"]["state"]
        card["status_parts"] = {
            "state": STATES[state] + ("" if state == "announced" else " " + german_date(measure["status"]["since"])),
            "bill_title": bill["title"],
            "citation": bill.get("citation") or bill["id"],
            "article": measure["article"],
        }
        card["bill_slug"] = bill["id"].replace("/", "-")
        card["topic"] = TOPIC_LABELS[measure["selection"]["household_relevance"]]
        card["follow_up"]["iso"] = measure["follow_up"]["date"]
        for src in card["detail"]["sources"]:
            src["role_label"] = ROLE_LABELS[src["role"]]
        card["vote"] = vote_view(bill)
        card["path"] = path_view(bill)
        card["approved"] = bool(measure["review"].get("approved"))
        cards.append(card)
    stand = max((b["retrieved"] for b in bills), default=date.today().isoformat())
    rows = sorted((bill_page(b, stand, country) for b in bills), key=lambda r: r["introduced"], reverse=True)
    return {
        "meta": {
            "data_as_of": stand,
            "data_as_of_text": german_date(stand) if stand else None,
            "bill_count": len(rows),
            "stage_counts": {k: sum(1 for r in rows if r["stage"] == k) for k, _ in STAGE_FILTERS},
            "type_counts": {k: sum(1 for r in rows if r["type"] == k) for k, _, _ in TYPE_FILTERS},
            "stage_filters": [{"id": k, "label": v} for k, v in STAGE_FILTERS],
            "type_filters": [{"id": k, "label": v} for k, v, _ in TYPE_FILTERS],
            "eu_filters": [{"id": k, "label": v} for k, v in EU_FILTERS],
            "eu_counts": {k: sum(1 for r in rows if r["eu"]["group"] == k) for k, _ in EU_FILTERS},
            "area_filters": [
                {"id": k, "label": label, "count": sum(1 for r in rows if any(a["id"] == k for a in r["areas"]))}
                for k, label, _ in AREAS.get(country, [])
            ],
            "happening_counts": {k: sum(1 for r in rows if k in r["happening"]) for k in ("upcoming", "decided", "new")},
        },
        "households": households_view(country),
        "cards": cards,
        "bills": rows,
    }


def write_site_data(out: pathlib.Path, country: str = "AT") -> list[pathlib.Path]:
    data = site_data(country)
    (out / "cards").mkdir(parents=True, exist_ok=True)
    for stale in (out / "cards").glob("*.json"):
        stale.unlink()
    written = []
    for card in data["cards"]:
        p = out / "cards" / f"{card['id']}.json"
        p.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(p)
    for name in ("meta", "households", "bills"):
        p = out / f"{name}.json"
        p.write_text(json.dumps(data[name], ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(p)
    return written
