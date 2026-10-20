from open_decisions_publish.format import (
    aggregate_text,
    amount_level_one,
    amount_level_two,
    german_date,
    german_number,
    round_level_one,
    share_of_income,
)


def test_rounding_to_10_below_1000_and_50_above():
    assert round_level_one(-217.5) == -220
    assert round_level_one(267.5) == 270
    assert round_level_one(1234) == 1250
    assert round_level_one(-1276) == -1300


def test_german_numbers_and_dates():
    assert german_number(1234.5, 1) == "1.234,5"
    assert german_number(70.9, 2) == "70,90"
    assert german_date("2025-06-16") == "16. Juni 2025"


def test_level_one_single_value_with_label_and_month():
    out = amount_level_one({"value": -217.5, "low": -217.5, "high": -217.5, "unit": "eur_per_year", "label": "estimated"})
    assert out["main"] == "minus 220 € (geschätzt)"
    assert out["sub"] == "etwa 18 € im Monat"


def test_level_one_range():
    out = amount_level_one({"value": -267.5, "low": -290, "high": -245, "unit": "eur_per_year", "label": "estimated"})
    assert out["main"] == "minus 250 bis 290 € (geschätzt)"
    assert out["sub"] == "etwa 21 bis 24 € im Monat"


def test_level_one_zero_and_not_quantifiable():
    assert amount_level_one({"value": 0, "unit": "eur_per_year", "label": "calculated"})["main"] == "ändert sich nicht (gerechnet)"
    out = amount_level_one({"value": None, "unit": "eur_per_year", "label": "not_quantifiable", "reason": "Tarifrechnung nötig."})
    assert out["main"] == "dazu gibt es keine belastbare Angabe (nicht bezifferbar)"
    assert out["sub"] == "Tarifrechnung nötig."


def test_level_one_positive():
    assert (
        amount_level_one({"value": 120, "low": 80, "high": 160, "unit": "eur_per_year", "label": "estimated"})["main"]
        == "plus 80 bis 160 € (geschätzt)"
    )


def test_level_two_unrounded_with_calculation():
    out = amount_level_two(
        {"value": -217.5, "low": -217.5, "high": -217.5, "unit": "eur_per_year", "label": "estimated", "calculation": "1 × 145 + 72,50"}
    )
    assert out == "minus 217,50 € (geschätzt); Rechenweg: 1 × 145 + 72,50"


def test_share_of_income_only_above_500():
    assert share_of_income(-660, 60000) == "rund 1,1 % des Einkommens"
    assert share_of_income(-400, 60000) is None
    assert share_of_income(-660, None) is None


def test_aggregate_text():
    assert (
        aggregate_text({"value": 2.0, "unit": "bn_eur_per_year", "label": "adopted", "year": 2025})
        == "2 Milliarden € pro Jahr (2025) (übernommen)"
    )
    assert aggregate_text({"value": 1200000, "unit": "households", "label": "adopted"}) == "1.200.000 Haushalte (übernommen)"
