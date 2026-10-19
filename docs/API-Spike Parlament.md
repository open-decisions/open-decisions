# API-Spike: Parlament, Budgetdienst, RIS

Oct 19, 2026 · Ergebnis eines 30-Minuten-Spikes vor der ersten Codezeile. Alle Aufrufe wurden tatsächlich ausgeführt; Beispiel ist die Klimabonus-Abschaffung.

## 1. Was die Parlaments-API liefert

**Liste aller Verhandlungsgegenstände einer Gesetzgebungsperiode**

```
POST https://www.parlament.gv.at/Filter/api/filter/data/101?js=eval&showAll=true
Content-Type: application/json
{"GP_CODE":["XXVIII"]}
```

- Antwort: `header` (Spaltendefinition) und `rows` (Arrays), 26.505 Zeilen für die XXVIII. GP, rund 17 MB, Lizenz CC BY 4.0
- Spalten u. a.: `Datum`, `Art` (RV, A, AUB, BNR …), `Betreff`, `Nummer`, `Status`, `HIS_URL`, `Fraktionen`, `THEMEN`, `EUROVOC`, `Abstimmung 3. Lesung`, `Dafür`, `Dagegen`, `Abstimmungstext`
- Kombinierte Filter wie `VHG` oder `ITYP` im Body wurden abgelehnt (count 0); es gibt keinen Endpunkt, der die gültigen Codes liefert. Pragmatisch: pro GP alles laden und lokal filtern, Delta über `Datum`
- Dieselbe API mit Liste `616` liefert den Fachinfos-Index inklusive aller Budgetdienst-Analysen (2.029 Zeilen: `Datum`, `Kategorie`, `Titel`, `uri`)

**Detailseite eines Verhandlungsgegenstands**

```
GET https://www.parlament.gv.at/gegenstand/XXVIII/I/69?json=TRUE
```

Felder unter `content`, die wir brauchen:

| Feld | Inhalt | Verwendung |
| --- | --- | --- |
| `status.number`, `status.description` | Stufe 1–5, Text mit Beschlussergebnis | Element 2 der Karte |
| `status.bgbllinks` | Link zum Bundesgesetzblatt und zum RIS-Kunsttext | Status „in Kraft", Quelle Rang 1 |
| `phase[].stages[]` | Einlangen NR, Ausschuss NR, Plenum NR, Einlangen BR, Ausschuss BR, Plenum BR; je Datum, Text, Links zu Sitzungen und Protokollstellen | Gesetzes-Tracker |
| `documents[]` | Gesetzestext (PDF und HTML), Erläuterungen, Textgegenüberstellung, „Vorblatt und WFA" (PDF, ggf. mehrere Teile) | Quellen Rang 1 und 2 |
| `vote.result[]` | pro Fraktion: Name, Mandate, `infavor` | „Wer hat dafür gestimmt" |
| `preconst[]` | Ministerialentwurf mit Kurzfassung (Ziele, Maßnahmen) | Stufe „Begutachtung" |
| `statements` | Stellungnahmen im Begutachtungsverfahren, Filterdefinition | später |
| `correspondence[]` | Parlamentskorrespondenz mit Datum und URL | neutrale Zusammenfassung, nicht die Regierungsbotschaft |
| `shortinfo` | Kurzinformation der Parlamentsdirektion als Liste der Maßnahmen | Startpunkt für die Maßnahmen-Liste einer Vorlage |
| `topics`, `headwords`, `eurovoc` | Schlagworte | Filter auf der Website |

## 2. Budgetdienst

- Analyseseite als JSON: `/fachinfos/budgetdienst/<slug>?json=TRUE`, enthält Überblickstext und PDF-Link
- Beispiel „Umsetzung weiterer Konsolidierungs- und Offensivmaßnahmen" (19.05.2025, 56 Seiten): Verteilungswirkung des Pakets nach Einkommensdezilen in Prozent des Haushaltseinkommens für 2025 bis 2029, Quelle laut Dokument: „eigene Berechnungen mit EUROMOD auf Grundlage von EU-SILC 2022"
- Keine Beispielhaushalte, keine Euro pro Haushaltstyp; die Dezil-Ergebnisse stehen in Grafiken und Tabellen (Seiten 45–52)
- Folge: Der Budgetdienst rechnet mit demselben Modell, das wir einsetzen wollen. Das stützt die Modellwahl und macht ihn zum natürlichen Gesprächspartner für den Beirat

## 3. RIS

```
GET https://data.bka.gv.at/ris/api/v2.6/Bundesrecht?Applikation=BrKons&Titel=Klimabonusgesetz
```

- Liefert pro Paragraf eine Norm-ID (NOR…), Inkrafttretens- und Außerkrafttretensdatum sowie XML/HTML/RTF-URLs
- Verwendung: „Was steht im Gesetz" aus dem konsolidierten Text, Zeitlichkeit (Befristungen, Außerkrafttreten) direkt aus den Metadaten

## 4. Befunde am Beispiel Klimabonus

1. Die Abschaffung ist **Artikel 71 des Budgetbegleitgesetzes 2025** (69 d.B.), ein Sammelgesetz mit 74 Artikeln. Gesetzestext: „Der Anspruch auf den regionalen Klimabonus besteht letztmalig für das Kalenderjahr 2024." Beschlossen am 16.06.2025 mit ÖVP, SPÖ, NEOS gegen FPÖ, GRÜNE; BGBl. I Nr. 25/2025.
2. Die **WFA** zu diesem Artikel (Seiten 357–369 von 408) enthält Ziele, Maßnahmen und den Finanzierungshaushalt des Bundes, aber keine Zahl der Betroffenen und keine Wirkung pro Haushalt. Die WFA ist schwächer als im Konzept angenommen; die Euro-Wirkung pro Haushalt kommt bei Pauschalbeträgen aus dem Gesetz selbst.
3. Das erste Konsolidierungspaket (BSMG 2025, 73/A) war ein **Initiativantrag** der Koalition: keine WFA, keine Begutachtung, keine Erläuterungen. Das Methodik-Handbuch (Abschnitt 2) nimmt Initiativanträge der Regierungsfraktionen seit 19.10.2026 gleichwertig auf; Belegquelle ist dann Gesetzestext plus Budgetdienst, das Fehlen der WFA wird auf der Karte benannt.
4. **Abstimmungsdaten pro Fraktion sind in der API** (206 Gegenstände mit Ergebnis der dritten Lesung in dieser GP). Die frühere Annahme, sie nur aus Protokollen extrahieren zu können, war falsch.
5. PDF-Extraktion funktioniert mit `pdftotext -layout`; die WFA zum BBG 2025 ergibt rund 1 MB Text, Tabellen bleiben lesbar.

## 5. Folgen für Schema v0

- Zwei Ebenen statt einer: **Vorhaben** (Verhandlungsgegenstand, Schlüssel `GP/ITYP/INR`, z. B. `XXVIII/I/69`) und **Maßnahme** (Artikel oder Teilregelung darin, z. B. Art. 71). Karten gibt es pro Maßnahme, Tracker und Abstimmung pro Vorhaben.
- Quellenangaben als Verweis auf API-Dokumente: Gesetzestext-HTML mit Artikelanker, WFA-PDF mit Seitenbereich, Budgetdienst-URI mit Seite, RIS-Norm-ID.
- Status aus `status.number` und `bgbllinks`; Zeitlichkeit aus RIS-Metadaten und Gesetzestext.
- Vorhabensarten: `RV` (Regierungsvorlage) und `A` (Initiativantrag) gleichwertig behandeln; bei `A` Feld `wfa: null` und Kennzeichnung auf der Karte.
