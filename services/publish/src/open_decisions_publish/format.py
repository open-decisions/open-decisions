import math
from datetime import date
from typing import Any

LABELS = {
    "calculated": "gerechnet",
    "adopted": "übernommen",
    "estimated": "geschätzt",
    "not_quantifiable": "nicht bezifferbar",
}
STATES = {
    "announced": "Angekündigt",
    "introduced": "Im Nationalrat eingebracht am",
    "passed": "Beschlossen am",
    "in_force": "In Kraft seit",
}
MONTHS = ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
NO_CHANGE = "ändert sich nicht"
NO_FIGURE = "dazu gibt es keine belastbare Angabe"


def round_half_up(value: float) -> int:
    return math.floor(abs(value) + 0.5) * (1 if value >= 0 else -1)


def round_level_one(value: float) -> int:
    step = 10 if abs(value) < 1000 else 50
    return round_half_up(abs(value) / step) * step * (1 if value >= 0 else -1)


def german_number(value: float, decimals: int = 0) -> str:
    return f"{abs(value):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def signed(value: float, decimals: int = 0) -> str:
    if value == 0:
        return "0"
    return ("minus " if value < 0 else "plus ") + german_number(value, decimals)


def german_date(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day}. {MONTHS[d.month - 1]} {d.year}"


def label_word(label: str) -> str:
    return LABELS[label]


def per_month(value: float) -> str:
    return f"etwa {german_number(abs(round_half_up(value / 12)))} € im Monat"


def amount_level_one(amount: dict[str, Any]) -> dict[str, str]:
    label = amount["label"]
    word = label_word(label)
    if label == "not_quantifiable" or amount.get("value") is None:
        return {"main": f"{NO_FIGURE} ({word})", "sub": amount.get("reason", "")}
    value = float(amount["value"])
    low, high = amount.get("low"), amount.get("high")
    if value == 0 and (low in (None, 0)) and (high in (None, 0)):
        return {"main": f"{NO_CHANGE} ({word})", "sub": ""}
    if label == "estimated" and low is not None and high is not None and low != high:
        lo, hi = sorted((round_level_one(float(low)), round_level_one(float(high))), key=abs)
        sign = "minus " if hi < 0 else "plus " if lo > 0 else ""
        main = f"{sign}{german_number(abs(lo))} bis {german_number(abs(hi))} € ({word})"
        sub = f"etwa {german_number(abs(round_half_up(lo / 12)))} bis {german_number(abs(round_half_up(hi / 12)))} € im Monat"
        return {"main": main, "sub": sub}
    rounded = round_level_one(value)
    return {"main": f"{signed(rounded)} € ({word})", "sub": per_month(rounded)}


def amount_level_two(amount: dict[str, Any]) -> str:
    label = amount["label"]
    if label == "not_quantifiable" or amount.get("value") is None:
        return f"{NO_FIGURE}: {amount.get('reason', '')}"
    parts = [f"{signed(float(amount['value']), 2)} € ({label_word(label)})"]
    if amount.get("low") is not None and amount.get("high") is not None and amount["low"] != amount["high"]:
        parts.append(f"Spannweite {signed(float(amount['low']), 2)} bis {signed(float(amount['high']), 2)} €")
    if amount.get("calculation"):
        parts.append(f"Rechenweg: {amount['calculation']}")
    return "; ".join(parts)


def share_of_income(value: float, disposable_income_year: float | None) -> str | None:
    if disposable_income_year is None or abs(value) <= 500 or disposable_income_year <= 0:
        return None
    share = abs(value) / disposable_income_year * 100
    return f"rund {german_number(share, 1)} % des Einkommens"


def aggregate_unit(unit: str) -> str:
    return {
        "eur_per_year": "€ pro Jahr",
        "eur_per_month": "€ pro Monat",
        "eur_once": "€ einmalig",
        "mio_eur_per_year": "Millionen € pro Jahr",
        "bn_eur_per_year": "Milliarden € pro Jahr",
        "bn_eur_total": "Milliarden € insgesamt",
        "percent_of_income": "% des Einkommens",
        "persons": "Personen",
        "households": "Haushalte",
    }[unit]


def aggregate_text(amount: dict[str, Any]) -> str:
    if amount.get("value") is None:
        return f"{NO_FIGURE} ({label_word(amount['label'])})"
    value = float(amount["value"])
    decimals = 1 if value != int(value) else 0
    unit = aggregate_unit(amount["unit"])
    year = f" ({amount['year']})" if amount.get("year") else ""
    return f"{german_number(value, decimals)} {unit}{year} ({label_word(amount['label'])})"
