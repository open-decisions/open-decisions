from open_decisions_publish.site import clean_press, duration, headline, stage_text


def test_headline_prefers_section_heading_and_skips_judgement_words():
    bill = {
        "title": "Gewerbeordnung, Änderung",
        "parliament_url": "https://www.parlament.gv.at/gegenstand/XXVIII/I/573",
        "summary": ["Vereinfachung von Anzeigepflichten"],
        "press": [
            {
                "title": "Neu im Wirtschaftsausschuss",
                "date": "2026-07-01",
                "url": "https://x/a#1",
                "heading": "Gewerbeordnungsreform zur Entbürokratisierung",
            },
        ],
    }
    h = headline(bill)
    assert h["text"] == "Vereinfachung von Anzeigepflichten"
    assert h["source"] == "Kurzinformation der Parlamentsdirektion"


def test_headline_falls_back_to_official_title():
    h = headline({"title": "Paketsteuergesetz", "parliament_url": "https://x", "press": [], "summary": []})
    assert h == {"text": "Paketsteuergesetz", "source": None, "url": None}


def test_clean_press_removes_body_prefix_and_process_phrase():
    assert clean_press("Nationalrat: Grünes Licht für Regelungen zur Versorgungssicherheit") == "Regelungen zur Versorgungssicherheit"


def test_duration_words():
    assert duration("2026-10-27", "2026-10-28") == "seit gestern"
    assert duration("2026-10-15", "2026-10-28") == "seit 13 Tagen"
    assert duration("2026-09-28", "2026-10-28") == "seit 4 Wochen"
    assert duration("2026-06-28", "2026-10-28") == "seit 4 Monaten"


def test_stage_text_committee_uses_first_committee_date():
    bill = {"status": {"stage": "committee"}, "introduced": "2026-10-01", "phases": [{"phase": "committee", "date": "2026-10-14"}]}
    assert stage_text(bill, "2026-10-28") == "wird seit 2 Wochen im Ausschuss beraten"


def test_published_stage_names_the_vote_and_gazette():
    bill = {
        "status": {"stage": "published", "gazette": "Bundesgesetzblatt I Nr. 84/2026"},
        "introduced": "2026-07-08",
        "phases": [],
        "vote": {"date": "2026-09-23"},
    }
    assert (
        stage_text(bill, "2026-10-28")
        == "gilt: im Nationalrat am 23. September 2026 beschlossen, kundgemacht im Bundesgesetzblatt I Nr. 84/2026"
    )


def test_next_date_text():
    from open_decisions_publish.site import next_date

    bill = {"phases": [{"phase": "committee", "chamber": "Nationalrat", "date": "2026-11-03"}]}
    assert next_date(bill, "2026-10-28") == {"date": "2026-11-03", "text": "Ausschuss des Nationalrats am 3. November 2026"}
