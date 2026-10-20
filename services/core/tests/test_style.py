from open_decisions_core.style import check_measure_style, flesch_amstad, sentences


def measure(**over):
    base = {
        "title": "Der Klimabonus wird nicht mehr ausgezahlt",
        "law_change": {"summary": "Den Klimabonus gab es bis 2024. Ab 2025 gibt es ihn nicht mehr.", "parameters": [{"name": "Betrag"}]},
        "unclear": ["Die Stufe des Wohnorts ist angenommen."],
        "assumptions": [{"what": "x", "why": "y", "alternative": "z"}],
    }
    base.update(over)
    return base


def test_clean_measure_has_no_errors():
    errors, _ = check_measure_style(measure())
    assert errors == []


def test_forbidden_word_outside_quote_is_error():
    errors, _ = check_measure_style(measure(unclear=["Das ist eine Entlastung für alle."]))
    assert any("forbidden word 'Entlastung'" in e for e in errors)


def test_forbidden_word_in_quote_is_allowed():
    errors, _ = check_measure_style(measure(said={"quote": "Diese Reform ist gerecht."}))
    assert errors == []


def test_long_sentence_and_title_and_punctuation():
    long = " ".join(["Wort"] * 21) + "."
    errors, _ = check_measure_style(measure(title=" ".join(["Wort"] * 9), law_change={"summary": long + " Wirklich?", "parameters": []}))
    assert any("title: 9 words" in e for e in errors)
    assert any("sentence has 21 words" in e for e in errors)
    assert any("question mark" in e for e in errors)


def test_sentences_respect_abbreviations():
    assert sentences("Siehe § 2 Abs. 2 KliBG. Das gilt ab 2025.") == ["Siehe § 2 Abs. 2 KliBG.", "Das gilt ab 2025."]


def test_flesch_prefers_short_words():
    assert flesch_amstad("Das ist gut. Es geht schnell.") > flesch_amstad(
        "Wirkungsorientierte Folgenabschätzungen berücksichtigen Verteilungswirkungen."
    )
