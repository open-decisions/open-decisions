from typing import Any

from open_decisions_core import DATA
from open_decisions_core.records import load
from open_decisions_publish.format import (
    STATES,
    aggregate_text,
    amount_level_one,
    amount_level_two,
    german_date,
    german_number,
    label_word,
    share_of_income,
)


def _bill_path(bill_id: str):
    return DATA / "bills" / (bill_id.replace("/", "-") + ".yaml")


def _households(jurisdiction: str) -> dict[str, dict[str, Any]]:
    country = jurisdiction.split("-")[0]
    data = load(DATA / "households" / f"{country}.yaml")
    return {h["id"]: h for h in data["households"]}


def status_line(measure: dict[str, Any], bill: dict[str, Any]) -> str:
    state = measure["status"]["state"]
    text = STATES[state]
    if state != "announced":
        text += " " + german_date(measure["status"]["since"])
    reference = f"{bill.get('title')}, {bill.get('citation') or bill['id']}"
    return f"{text}. {reference.rstrip('.')}."


def vote_text(bill: dict[str, Any]) -> str | None:
    vote = bill.get("vote")
    if not vote:
        return None
    yes = [r["party"] for r in vote["result"] if r["in_favor"]]
    no = [r["party"] for r in vote["result"] if not r["in_favor"]]
    return f"Nationalrat, {german_date(vote['date'])}: dafür {', '.join(yes)}; dagegen {', '.join(no)}."


def card_view(measure: dict[str, Any]) -> dict[str, Any]:
    bill = load(_bill_path(measure["bill"]))
    households = _households(measure["jurisdiction"])
    sources = {s["id"]: s for s in measure["sources"]}

    rows = []
    for row in measure["effects"]["households"]:
        h = households[row["household"]]
        short, long_ = amount_level_one(row["short_term"]), amount_level_one(row["long_term"])
        share = share_of_income(float(row["short_term"].get("value") or 0), h.get("disposable_income_year"))
        rows.append(
            {
                "id": h["id"],
                "label": h["label"],
                "short": short,
                "long": long_,
                "share": share,
                "note": row.get("note"),
                "detail_short": amount_level_two(row["short_term"]),
                "detail_long": amount_level_two(row["long_term"]),
            }
        )

    def refs(items):
        return [{"title": sources[r["source"]]["title"], "url": sources[r["source"]]["url"], "ref": r["ref"]} for r in items]

    said = measure["said"]
    view = {
        "id": measure["id"],
        "lang": measure["lang"],
        "title": measure["title"],
        "status": status_line(measure, bill),
        "said": {
            "quote": said["quote"],
            "speaker": said["speaker"],
            "role": said["role"],
            "date": german_date(said["date"]),
            "sources": refs(said["sources"]),
        },
        "law": measure["law_change"]["summary"],
        "years": {"short": measure["timing"]["first_full_year"], "long": measure["timing"]["fifth_year"]},
        "households": rows,
        "unclear": measure["unclear"],
        "follow_up": {"date": german_date(measure["follow_up"]["date"]), "what": measure["follow_up"]["what"]},
        "detail": {
            "parameters": [
                {
                    "name": p["name"],
                    "old": _param_value(p.get("old"), p.get("unit")),
                    "new": _param_value(p.get("new"), p.get("unit")),
                    "applies_from": p["applies_from"],
                    "sources": refs(p["sources"]),
                }
                for p in measure["law_change"]["parameters"]
            ],
            "affected": {
                "who": measure["affected"]["who"],
                "condition": measure["affected"].get("condition"),
                "count": aggregate_text(measure["affected"]["count"]),
            },
            "timing": measure["timing"],
            "assumptions": measure["assumptions"],
            "aggregate": [{"description": a["description"], "text": aggregate_text(a["amount"])} for a in measure["effects"]["aggregate"]],
            "distribution": measure["effects"].get("distribution"),
            "contradictions": measure.get("contradictions", []),
            "open_questions": measure.get("open_questions", []),
            "vote": vote_text(bill),
            "sources": [{**s, "retrieved": german_date(s["retrieved"]), "role": s["role"]} for s in measure["sources"]],
            "changelog": [{**c, "date": german_date(c["date"])} for c in measure["changelog"]],
            "review": measure["review"],
        },
    }
    view["detail"]["distribution_label"] = (
        label_word(view["detail"]["distribution"]["label"]) if view["detail"].get("distribution") else None
    )
    return view


def _param_value(value: Any, unit: str | None) -> str:
    if value is None:
        return "–"
    if isinstance(value, int | float):
        decimals = 0 if float(value) == int(value) else (2 if abs(value) < 100 else 1)
        return f"{german_number(float(value), decimals)} {unit or ''}".strip()
    return str(value)
