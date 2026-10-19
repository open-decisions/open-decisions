import json
import pathlib
from datetime import date, datetime

import pytest
from open_decisions_core.records import check
from open_decisions_ingest_at.client import list_rows, parse_his_url
from open_decisions_ingest_at.transform import bill_from_item, eli_from_bgbl, record_from_bill

FIXTURES = pathlib.Path(__file__).resolve().parents[3] / "fixtures" / "parlament"
FETCHED = datetime(2026, 10, 19, 22, 0, 0)


def item(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_government_bill_69():
    bill = bill_from_item(item("item_XXVIII_I_69.json"), FETCHED)
    assert bill["id"] == "AT/XXVIII/I/69"
    assert bill["type"] == "government_bill"
    assert bill["introduced"] == date(2025, 5, 13)
    assert bill["stage"] == "published"
    assert bill["gazette"] == "Bundesgesetzblatt I Nr. 25/2025"
    assert bill["eli"] == "https://www.ris.bka.gv.at/eli/bgbl/I/2025/25"
    assert bill["vote"]["date"] == date(2025, 6, 16)
    assert {r["party"]: r["in_favor"] for r in bill["vote"]["result"]} == {
        "ÖVP": True,
        "SPÖ": True,
        "NEOS": True,
        "FPÖ": False,
        "GRÜNE": False,
    }
    assert sum(r["seats"] for r in bill["vote"]["result"]) == 183
    assert bill["documents"]["impact_assessment_pdf"] == ["https://www.parlament.gv.at/dokument/XXVIII/I/69/imfname_1685635.pdf"]
    assert bill["documents"]["law_text_html"].endswith("fnameorig_1685631.html")
    assert [p["citation"] for p in bill["pre_parliamentary"]] == ["15/ME", "16/ME"]
    assert bill["eurovoc"] == ["Öffentliche Finanzen und Haushaltspolitik"]
    phases = [p["phase"] for p in bill["phases"]]
    assert phases[0] == "introduced" and "second_chamber_plenary" in phases


def test_members_bill_73_has_no_impact_assessment():
    bill = bill_from_item(item("item_XXVIII_A_73.json"), FETCHED)
    assert bill["type"] == "members_bill"
    assert bill["id"] == "AT/XXVIII/A/73"
    assert "impact_assessment_pdf" not in bill["documents"]
    assert "law_text_html" in bill["documents"]
    assert bill["stage"] == "published"
    assert bill["pre_parliamentary"] == []


@pytest.mark.parametrize("name", ["item_XXVIII_I_69.json", "item_XXVIII_I_91.json", "item_XXVIII_A_73.json"])
def test_record_validates(name):
    bill = bill_from_item(item(name), FETCHED)
    record = record_from_bill(bill, {"measures": [], "budget_office_analyses": []})
    assert check(record) == []


def test_curated_fields_are_preserved():
    bill = bill_from_item(item("item_XXVIII_I_69.json"), FETCHED)
    record = record_from_bill(
        bill,
        {
            "measures": ["at-2025-klimabonus"],
            "budget_office_analyses": [{"title": "x", "date": "2025-05-19", "url": "https://example.org"}],
        },
    )
    assert record["measures"] == ["at-2025-klimabonus"]
    assert record["budget_office_analyses"][0]["title"] == "x"


def test_list_rows_and_keys():
    rows = list_rows(item("list_XXVIII_subset.json"))
    keys = {parse_his_url(r["HIS_URL"]) for r in rows}
    assert ("XXVIII", "I", "69") in keys
    assert ("XXVIII", "A", "73") in keys


def test_eli():
    assert eli_from_bgbl("Bundesgesetzblatt I Nr. 7/2025") == "https://www.ris.bka.gv.at/eli/bgbl/I/2025/7"
    assert eli_from_bgbl("Kunsttext") is None
