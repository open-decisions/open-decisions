import pathlib
import re

from open_decisions_core import DATA
from open_decisions_core.records import load
from open_decisions_publish.cards import card_view
from open_decisions_publish.cli import render

ELEMENTS = ["Was wurde gesagt", "Was steht im Gesetz", "Was heißt das für dich", "Was ist unklar", "Nachschauen"]


def test_klimabonus_view_model():
    card = card_view(load(DATA / "measures" / "at-2025-klimabonus.yaml"))
    assert card["title"] == "Der Klimabonus wird nicht mehr ausgezahlt"
    assert card["status"].startswith("In Kraft seit 30. Juni 2025.")
    assert len(card["households"]) == 7
    assert card["households"][0]["short"]["main"] == "minus 220 € (geschätzt)"
    assert card["detail"]["vote"].startswith("Nationalrat, 16. Juni 2025: dafür ÖVP, SPÖ, NEOS; dagegen FPÖ, GRÜNE.")


def test_render_all_cards_with_seven_elements_in_order(tmp_path: pathlib.Path):
    files = render(tmp_path)
    htmls = [f for f in files if f.suffix == ".html" and f.name != "index.html"]
    assert len(htmls) == len(list((DATA / "measures").glob("*.yaml")))
    for f in htmls:
        text = f.read_text(encoding="utf-8")
        positions = [text.index(e) for e in ELEMENTS]
        assert positions == sorted(positions), f.name
        assert re.search(r"\((gerechnet|übernommen|geschätzt|nicht bezifferbar)\)", text), f.name
        assert "–290" not in text
        assert "-290" not in text
