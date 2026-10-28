from open_decisions_ingest_at.eu import DIRECTIVE, REGULATION, act, acts, directive_celex, regulation_celex, relation


def test_celex_from_directive_forms():
    cases = {
        "Richtlinie (EU) 2019/1152": "32019L1152",
        "Richtlinie 2014/65/EU": "32014L0065",
        "Richtlinie 2006/112/EG": "32006L0112",
        "Richtlinie 93/13/EWG": "31993L0013",
        "Richtlinie 2024/1260/EU": "32024L1260",
    }
    for text, expected in cases.items():
        m = DIRECTIVE.search(text)
        assert m is not None
        assert directive_celex(m) == expected, text


def test_celex_from_regulation_forms():
    cases = {
        "Verordnung (EU) 2023/1542": "32023R1542",
        "Verordnung (EU) Nr. 575/2013": "32013R0575",
        "Verordnung (EG) Nr. 1907/2006": "32006R1907",
        "Verordnung (EU) 2024/2748": "32024R2748",
    }
    for text, expected in cases.items():
        m = REGULATION.search(text)
        assert m is not None
        assert regulation_celex(m) == expected, text


def test_acts_need_transposition_context():
    text = "Dieses Gesetz dient der Umsetzung der Richtlinie (EU) 2019/1152. Im Übrigen gilt die Verordnung (EU) 2016/679."
    assert acts(text) == [("32019L1152", "transposed")]
    assert acts("Umsetzungshinweis: CELEX-Nr. 32024L1346") == [("32024L1346", "transposed")]


def test_relation_national():
    wfa = (
        "Verhältnis zu den Rechtsvorschriften der Europäischen Union\n"
        "Die vorgesehenen Regelungen fallen nicht in den Anwendungsbereich des Rechts der Europäischen Union\nBesonderheiten"
    )
    r = relation([("https://x/wfa.pdf", wfa)])
    assert r["kind"] == "national"
    assert r["acts"] == []
    assert r["statements"][0]["text"].startswith("Die vorgesehenen Regelungen fallen nicht")


def test_relation_transposition_with_goes_beyond():
    wfa = (
        "Verhältnis zu den Rechtsvorschriften der Europäischen Union\n"
        "Das Vorhaben geht über eine verpflichtende Umsetzung zwingender Vorschriften des Unionsrechtes hinaus\nBesonderheiten"
    )
    law = "Mit diesem Bundesgesetz wird die Richtlinie (EU) 2023/2226 umgesetzt. Zur Umsetzung der Richtlinie (EU) 2023/2226 ..."
    r = relation([("https://x/wfa.pdf", wfa), ("https://x/law.html", law)])
    assert r["kind"] == "transposes_directive"
    assert r["goes_beyond"] is True
    assert [a["celex"] for a in r["acts"]] == ["32023L2226"]


def test_act_links():
    a = act("32019L1152", "transposed")
    assert a["eurlex_url"] == "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:32019L1152"
    assert a["eli"] == "http://data.europa.eu/eli/dir/2019/1152/oj"
    assert a["label"] == "Richtlinie 2019/1152"


def test_impact_assessment_statement_wins_over_text_matches():
    wfa = (
        "Verhältnis zu den Rechtsvorschriften der Europäischen Union\n"
        "Die vorgesehenen Regelungen fallen nicht in den Anwendungsbereich des Rechts der Europäischen Union\nBesonderheiten"
    )
    law = "In Durchführung der Verordnung (EU) 2016/679 werden Daten verarbeitet."
    r = relation([("https://x/wfa.pdf", wfa), ("https://x/law.html", law)])
    assert r["kind"] == "national"
    assert r["acts"] == []


def test_text_matches_used_without_statement():
    r = relation([("https://x/antrag.html", "Dieses Gesetz dient der Umsetzung der Richtlinie (EU) 2022/2464.")])
    assert r["kind"] == "transposes_directive"
    assert [a["celex"] for a in r["acts"]] == ["32022L2464"]


def test_lower_case_accompanying_wording():
    r = relation([("https://x/law.html", "Zweck ist die Erlassung begleitender Regelungen zur Verordnung (EU) 2023/1542 über Batterien.")])
    assert [a["celex"] for a in r["acts"]] == ["32023R1542"]
