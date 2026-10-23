import json
import pathlib
from typing import Any

from open_decisions_core import DATA
from open_decisions_core.records import load
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


def bill_row(bill: dict[str, Any]) -> dict[str, Any]:
    stage = bill["status"]["stage"]
    kind = next(t[2] for t in TYPE_FILTERS if t[0] == bill["type"])
    return {
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
        card["topic"] = TOPIC_LABELS[measure["selection"]["household_relevance"]]
        card["follow_up"]["iso"] = measure["follow_up"]["date"]
        for src in card["detail"]["sources"]:
            src["role_label"] = ROLE_LABELS[src["role"]]
        card["vote"] = vote_view(bill)
        card["path"] = path_view(bill)
        card["approved"] = bool(measure["review"].get("approved"))
        cards.append(card)
    rows = sorted((bill_row(b) for b in bills), key=lambda r: r["introduced"], reverse=True)
    stand = max((b["retrieved"] for b in bills), default=None)
    return {
        "meta": {
            "data_as_of": stand,
            "data_as_of_text": german_date(stand) if stand else None,
            "bill_count": len(rows),
            "stage_counts": {k: sum(1 for r in rows if r["stage"] == k) for k, _ in STAGE_FILTERS},
            "type_counts": {k: sum(1 for r in rows if r["type"] == k) for k, _, _ in TYPE_FILTERS},
            "stage_filters": [{"id": k, "label": v} for k, v in STAGE_FILTERS],
            "type_filters": [{"id": k, "label": v} for k, v, _ in TYPE_FILTERS],
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
