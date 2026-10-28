from open_decisions_ingest_at.press import json_url, release_parts, section_heading

BODY = (
    '<div class=pk ><a id="XXVIII_NRSITZ_00027"></a><div class="c_2"><p>Wien (PK) Einleitung</p></div>'
    '<a id="XXVIII_I_00091"></a><h2>Fortsetzung der Budgetsanierung: '
    "Anstieg der KV-Beitr&auml;ge f&uuml;r Pensionist:innen </h2><p>Text</p>"
    '<a id="XXVIII_I_00069"></a><p>Kein eigener Abschnittstitel</p></div>'
)


def test_section_heading_after_anchor():
    assert section_heading(BODY, "XXVIII_I_00091") == "Fortsetzung der Budgetsanierung: Anstieg der KV-Beiträge für Pensionist:innen"
    assert section_heading(BODY, "XXVIII_I_00069") is None
    assert section_heading(BODY, "XXVIII_I_00001") is None


def test_release_parts_and_url():
    payload = {"content": [{"data": {"title": "Zweite Runde der Budgetsanierung "}}, {"data": {"text": BODY}}]}
    title, body = release_parts(payload)
    assert title == "Zweite Runde der Budgetsanierung"
    assert body == BODY
    assert json_url("https://www.parlament.gv.at/aktuelles/pk/jahr_2025/pk0438#XXVIII_I_00091") == (
        "https://www.parlament.gv.at/aktuelles/pk/jahr_2025/pk0438?json=TRUE"
    )
