# Projektkonzept: Politische Entscheidungen verständlich bewertet

Oct 18, 2026 · @Valcome Innovation GmbH

## Die Idee

Politische Entscheidungen werden positiv verkauft, aber was sie konkret bringen, bleibt für die meisten Menschen unklar. Das Projekt erklärt pro Entscheidung, was sie kurz- und langfristig für verschiedene Einkommensschichten bedeutet – so neutral und wissenschaftlich fundiert wie möglich, aber für jede:n verständlich.

- **Start:** Österreich, Regierungsentscheidungen (öffentliche Daten vorhanden)
- **Später:** Wahl- und Parteiprogramme
- **Nicht im MVP:** Makroökonomische Simulationen; Verteilungswirkung ja, Wirtschaftsmodelle nein
- **Kein Profit:** Laufende Kosten plus ein Teilzeit-Einkommen sind das Ziel
- **Lebendig:** Nutzer:innen geben Feedback, melden Betroffenheit, stellen Fragen

## Was es bereits gibt

Teile der Idee existieren, die Kombination aus laufender Verteilungsrechnung und verständlicher Erklärung nicht.

| Wer | Was | Was fehlt |
| --- | --- | --- |
| [ZEW Mannheim](https://ftp.zew.de/pub/zew-docs/gutachten/Bundestagswahlprogramme_ZEW_2025.pdf) mit SZ | Rechnet Wahlprogramme nach Einkommensdezilen durch (Modell ZEW-EviSTA) | Nur zu Wahlen, nur bezifferbare Maßnahmen, 80-seitige PDFs |
| DIW, ifo | Verteilungsanalysen zu Steuer- und Transferreformen in Deutschland | Fachpublikum, nicht laufend |
| CPB (Niederlande), IFS (UK) | Internationale Vorbilder, CPB rechnet alle Wahlprogramme systematisch durch | Nicht für Österreich |
| Budgetdienst des Parlaments (AT) | Unabhängige Analysen zu Budget- und Gesetzesvorhaben, teils nach Dezilen | Sperrige Form, kein Dialog, keine Beispielhaushalte |
| [wahl.chat](https://www.tum.de/aktuelles/alle-meldungen/pressemitteilungen/details/technologie-fuer-teilhabe) | KI-Tool zu Parteipositionen, über 150.000 Nutzer:innen zur Bundestagswahl 2025 | Fasst zusammen, was Parteien wollen; rechnet keine Wirkung |
| Wahl-O-Mat, Wahlkabine | Positionsvergleich | Keine Wirkungsanalyse |

Der politische Bedarf ist erkannt: Die Linke hat im Februar 2026 einen verpflichtenden [Verteilungs-Check](https://dserver.bundestag.de/btd/21/040/2104004.pdf) für Gesetze im Bundestag beantragt.

**Die Lücke:** Niemand verbindet laufend, nicht nur zu Wahlen, seriöse Verteilungsrechnung mit allgemeinverständlicher Erklärung und kurz-/langfristiger Einordnung.

## Technische Basis

Die Zahlen kommen aus einem Mikrosimulationsmodell, nicht aus dem Sprachmodell. Die KI findet, übersetzt, strukturiert und erklärt – und sagt ehrlich, wo es keine belastbaren Daten gibt. Eine KI, die Verteilungseffekte selbst „schätzt", wäre das Gegenteil von wissenschaftlich.

**Vorbild: [PolicyEngine](https://digitalgovernmenthub.org/ecosystem/directory/policyengine/) (US/UK)**

- Open-Source-Mikrosimulation, nutzbar als Python-Paket, Web-API und Web-App
- KI seit 2023 für Erklärungen und What-if-Szenarien, inzwischen agentische KI integriert
- Offizielles Claude-Code-Plugin mit Agents und Skills
- Designprinzip: Modell ist expliziter Input mit eigenen Fehlerbalken, nie Ground Truth
- Wird inzwischen im Büro des britischen Premierministers für schnelle Policy-Analysen genutzt

**Offene Modelle für den deutschsprachigen Raum**

| Modell | Abdeckung | Vorteil | Haken |
| --- | --- | --- | --- |
| EUROMOD (EU-Kommission/JRC) | Alle EU-Länder, inkl. AT und DE | Frei nutzbar, Schnittstellen für Python/R, Hypothetical Household Tool ohne Mikrodaten | Dezile brauchen EU-SILC-Forschungsdatenzugang |
| GETTSIM | Deutschland | Open-Source-Python, direkt als Tool anbindbar | Nur DE; SOEP-Daten nur mit Vertrag |
| OpenFisca | Framework, länderunabhängig | Basis von PolicyEngine | Eigenes AT-Modell wäre enormer Aufwand |
| ZEW-EviSTA | Deutschland | Referenzmodell der ZEW-Analysen | Intern, nicht zugänglich |

Für Österreich gibt es kein offenes nationales Modell; WIFO und IHS haben proprietäre. **Entscheidung: EUROMOD, Start mit Österreich.**

**Drei reale Hürden**

1. Datenzugang, nicht Software: Modelle sind offen, repräsentative Haushaltsdaten nicht. Lösbar über Forschungsdatenzentren, idealerweise mit Uni-Anbindung.
2. Abdeckung: Mikrosimulation kann Steuern, Transfers, Mindestlohn, Beihilfen. Nicht bezifferbar sind z. B. Mietpreisbremse oder Bürokratieabbau – dort ehrlich „nicht bezifferbar" sagen.
3. Übersetzungsproblem: „Wir entlasten die Mitte" muss in Parameter übersetzt werden. Diese Annahmen sind die größte Angriffsfläche; sie müssen sichtbar sein und von Menschen geprüft werden.

## Datenquellen in Österreich

Österreich hat bessere öffentliche Grundlagen als Deutschland – drei Quellen tragen den MVP.

| Quelle | Was sie liefert | Wo |
| --- | --- | --- |
| Wirkungsorientierte Folgenabschätzung (WFA) | Pflicht bei jeder Regierungsvorlage; finanzielle Auswirkungen, oft Angaben zu Betroffenen | parlament.gv.at, Materialienpaket (PDF) |
| Budgetdienst des Parlaments | Unabhängige Analysen zu Budget- und Gesetzesvorhaben, teils mit Verteilungswirkung nach Dezilen | parlament.gv.at |
| EUROMOD Hypothetical Household Tool (HHoT) | Effekte für selbst definierte Beispielhaushalte, ohne EU-SILC-Zugang | EUROMOD-Software |
| EU-SILC (Statistik Austria) | Repräsentative Haushaltsdaten für echte Dezile | Forschungsdatenzugang nötig – später |
| Offizielle Pressetexte (BKA, Ministerien) | Die „Verkaufsbotschaft" zur Maßnahme | bundeskanzleramt.gv.at, APA-OTS |

## Konzept und MVP-Features

Alles hängt an einem strukturierten Datenobjekt pro politischer Entscheidung. Das LLM befüllt den Entwurf aus den Quellen, ein Mensch gibt ihn frei. Bei 20–30 haushaltsrelevanten Maßnahmen pro Jahr ist das überschaubar.

**Das Kernobjekt „Maßnahme"**

- Was wurde beschlossen: Gesetzestext, Datum, Status (angekündigt / beschlossen / in Kraft)
- Was wurde kommuniziert: die offizielle Verkaufsbotschaft
- Welche Parameter ändern sich (z. B. Klimabonus 290 € → 0 €)
- Wer ist betroffen: Haushaltstyp, Einkommen, Alter, Region
- Was sagen WFA und Budgetdienst
- Zeitlichkeit: wirkt sofort / ab Jahr X / befristet / nicht valorisiert

**Features für Nutzer:innen**

1. **Maßnahmen-Karte** mit vier Teilen: Was wurde gesagt · Was steht im Gesetz · Was heißt das für dich · Was ist unklar. Die Teilung macht die Lücke zwischen Verkauf und Wirkung sichtbar, ohne zu werten.
2. **Beispielhaushalte statt Dezile**: 6–8 Archetypen (Alleinerziehende mit 2.100 € brutto, Pensionistin mit Ausgleichszulage, Doppelverdiener mit zwei Kindern, Student mit Nebenjob, Selbstständiger …), jede Maßnahme in Euro pro Jahr gerechnet. Verständlicher als „3. Dezil" und mit HHoT machbar.
3. **„Mein Haushalt"**: grobe Eingabe von Einkommen, Haushaltsgröße, Wohnsituation; Rechnung lokal im Browser, keine Speicherung.
4. **Kurzfristig / langfristig als zwei Spalten**: ohne Makro-Modelle heißt langfristig: fehlende Valorisierung, auslaufende Übergangsfristen, endende Befristungen. Reine Arithmetik, oft der eigentliche Punkt.
5. **Konfidenz-Label** pro Zahl: „Gerechnet (EUROMOD)" · „Aus Budgetdienst/WFA übernommen" · „Nicht bezifferbar". Das dritte Label oft zu nutzen schafft Glaubwürdigkeit.

**Lebendig durch User-Feedback**

- **Betroffenheits-Meldungen**: „Trifft mich das? Ja / Nein / Weiß nicht" plus Freitext – zeigt fehlende Haushaltstypen
- **Fehler-Flags mit Begründungspflicht**: jede Zahl meldbar, Meldungen in öffentlicher Issue-Liste
- **Follow-up nach einem Jahr**: Was ist real passiert (Budgetvollzug, Statistik Austria)? Nutzer:innen können sich dafür eintragen – die stärkste Antwort auf „positiv verkauft, nichts passiert"
- **Fragen-Sammlung**: LLM antwortet nur aus hinterlegten Quellen; Unbeantwortbares landet in einer Recherche-Liste

**Neutralitätsmechanik (von Anfang an)**

- Alle Annahmen pro Maßnahme öffentlich und versioniert
- Wirkung in Euro und Betroffenen beschreiben, nie in „gerecht / ungerecht"
- Methodenbeirat, auch wenn er anfangs aus zwei Personen besteht (WU, JKU, Uni Graz)
- Finanzierung offenlegen
- Zweites Augenpaar aus der Verteilungsökonomie, das Annahmen gegenzeichnet – wichtiger als jeder Vereinsfunktionär

**Kostenrealität**

Fast alles wird vorab generiert: Karten, Beispielhaushalte und Erklärungen entstehen einmal beim Einpflegen. Teuer ist nur der freie Chat – begrenzt durch kleines Modell, Antworten nur aus Quellen, Rate-Limit, Cache. Realistisch: Hosting 20–60 €/Monat, LLM 50–300 €/Monat bei einigen tausend Nutzer:innen, EUROMOD kostenlos. Der eigentliche Kostenfaktor ist Arbeitszeit.

## Finanzierung

Infrastruktur ist billig, Förderung muss die Arbeitszeit decken. Antrag Nummer eins ist netidee.

**Förderungen**

| Förderung | Passung | Betrag | Anmerkung |
| --- | --- | --- | --- |
| [netidee](https://www.netidee.at) (Internet Stiftung) | Sehr hoch: Open Source, gesellschaftlicher Mehrwert, Sonderpreis „Digitale Entscheidungsfindung" gab es bereits | bis 60.000 € | Details im nächsten Abschnitt |
| NGI Zero (EU, über NLnet) | Hoch für den technischen Baustein EUROMOD-Anbindung | 5.000–50.000 € | Mehrere Calls pro Jahr, kurzer englischer Antrag |
| CERV (EU „Bürger, Gleichstellung, Rechte und Werte") | Demokratische Teilhabe ist Kernthema | höher | Aufwendig, eher Jahr 2 mit Partnern |
| AK-Digifonds, Wirtschaftsagentur Wien | Calls für digitale Zivilgesellschaft | variabel | AK-Geld könnte Neutralitätsimage schaden – transparent abwägen |
| Stiftungen: ERSTE Stiftung, Luminate, Civitates, Mercator | Demokratie / Zivilgesellschaft | variabel | Steigen ein, wenn etwas läuft und Nutzer hat |

**Laufende Einnahmen ohne Profit**

- **Mitgliedschaften / Dauerspenden**: stabilste Säule (Vorbilder: Dossier, Momentum Institut), aber erst ab Sichtbarkeit
- **Medienkooperation** (Standard, Falter, ORF, Profil): Analysen liefern, Reichweite oder kleines Honorar – wie ZEW mit der SZ
- **Uni-Anbindung** (WU, JKU, Uni Graz, Uni Wien): erleichtert EU-SILC-Zugang, bringt Legitimation, kann über FFG/FWF-Projekt eine Anstellung ermöglichen – der ehrlichste Weg zu „etwas Geld zum Überleben" in den ersten zwei Jahren

**Rechtsform**

Gemeinnütziger Verein, sobald nötig (siehe Abschnitt Verein). Spendenabsetzbarkeit wurde 2024 ausgeweitet; ob Bildung/Demokratie darunterfällt, mit Steuerberater prüfen – lohnt erst bei echtem Spendenaufkommen.

## netidee im Detail

Einreichung allein als Privatperson ist möglich, auch mit nebenberuflicher Selbstständigkeit. Geprüft anhand der [Förderbedingungen Call 21 (2026)](https://www.netidee.at/sites/default/files/2026-03/Call%2021%20F%C3%B6rderbedingungen%20%282026%29.pdf).

| Punkt | Regelung |
| --- | --- |
| Antragsberechtigt | Volljährige natürliche Personen mit Wohnsitz in Österreich; juristische Personen mit österreichischer Firmenadresse |
| Förderhöhe | Bis 60.000 € pro Projekt (Folder 2025), Restfinanzierung ggf. selbst |
| Eigenleistung | Max. 45 €/h – gleich für Privatpersonen, Firmeneigentümer:innen und Vereinsfunktionär:innen; 60.000 € ≈ 1.300 h ≈ ein Jahr Halbzeit |
| Laufzeit | Längstens 18 Monate; keine rückwirkende Förderung, nur Kosten nach Fördervereinbarung |
| Auszahlung | Drei Raten: nach Detailplanung, nach Zwischenbericht, nach Endbericht – Vorfinanzierung nötig |
| Haftung | Antragsteller:in haftet persönlich für erhaltene Raten |
| Lizenzen | Software: OSI-approbiert; Inhalte: CC-BY oder CC-BY-SA |
| Pflichten | Projektseite auf netidee.at, Blogbeitrag mindestens alle drei Monate, Zwischen- und Endbericht, Bewerbungsvideo im Antrag |
| Bewertung | Innovationspotenzial, Wahrscheinlichkeit des erfolgreichen Abschlusses, Verwertungschancen, Antragsqualität |
| Call-Rhythmus | Start meist März, Frist Frühsommer, Vergabe Herbst – realistisch Call 22 im Frühjahr 2027 |

**Offene Fragen**

- [ ] KESt: In den Bedingungen ist von KESt-Überweisungen und KESt-Bestätigungen die Rede – klären, ob netto weniger ankommt (antrag@netidee.at, Steuerberater)
- [ ] Einreichung als Privatperson oder über das Einzelunternehmen – steuerlich prüfen
- [ ] Call-22-Termine, sobald veröffentlicht

Der Beirat sieht gern, dass schon begonnen wurde und dass es nach Projektende weitergeht – Vorarbeiten, Beirat und Uni-/Vereinsplan stärken den Antrag.

## Verein

Ein Verein braucht vier Namen, aber niemand muss inhaltlich mitarbeiten – und für den Start ist er noch nicht nötig.

**Mindestanforderungen (Vereinsgesetz)**

- Zwei Gründer:innen
- Leitungsorgan aus mindestens zwei Personen (z. B. Obmann/Obfrau und Kassier:in)
- Zwei Rechnungsprüfer:innen, nicht im Vorstand
- Rollen dürfen formal sein; Rechnungsprüfer:innen müssen aber jährlich tatsächlich prüfen
- Vorstand haftet dem Verein bei grober Fahrlässigkeit – bei kleinem gemeinnützigem Verein ohne Schulden praktisch kein Thema, aber vorher offen ansprechen

**Empfehlung:** Erst gründen, wenn Geld fließt oder ein Partner (Uni, Medium, Stiftung) eine juristische Person braucht. netidee geht als Privatperson. Das zweite Augenpaar für die Neutralität (Ökonom:in im Beirat) ist früher wichtig als der Kassier.

## Bedarf

Die Daten zeigen ein Vertrauensproblem, das entlang des Einkommens verläuft, und ein Themenfeld (Teuerung, Verteilung), in dem Menschen genau die Frage stellen, die das Projekt beantwortet: Was heißt das für mich? Dazu kommt ein Nachfragebeleg aus einem verwandten Tool und eine Finanzierungswarnung aus demselben Tool.

**Vertrauen und Repräsentation – [Demokratie Monitor 2025](https://www.foresight.at/fileadmin/user_upload/pdf/2025_Demokratie-Monitor_Erste-Ergebnisse_PK.pdf) (Foresight, n = 2.005)**

| Befund | Wert 2025 | Vergleich |
| --- | --- | --- |
| Politisches System funktioniert gut | 35 % | 64 % im Jahr 2018 |
| Vertrauen in Bundesregierung | 32 % | Parlament 41 %, Verwaltung 60 %, Gerichte 64 % |
| Gesetze kommen regelkonform zustande | 76 % | stabil seit 2018 |
| „Menschen wie ich sind im Parlament gut vertreten" | 31 % | 61 % im Jahr 2018; unteres Einkommensdrittel 17 % |
| System funktioniert gut, nach Einkommensdrittel | unten 19 %, Mitte 38 %, oben 50 % | unteres Drittel 2020: 43 % |
| Wichtigstes politisches Anliegen | Teuerung 35 %, Verteilungsfragen 23 % | über alle Parteigrenzen hinweg an erster Stelle |
| Mussten beim Lebensmitteleinkauf sparen | 47 % | unteres Drittel 79 %, oberes 19 % |

Lesart für das Projekt: Die Menschen zweifeln nicht am Verfahren (76 % halten die Gesetzgebung für regelkonform), sondern daran, ob die Ergebnisse für sie gemacht sind. Genau das ist nicht Meinung, sondern prüfbar – pro Maßnahme, pro Haushaltstyp. Der stärkste Hebel liegt im unteren und mittleren Drittel, dort ist das Misstrauen am höchsten und die Betroffenheit durch Teuerung und Verteilungsentscheidungen am größten.

**Nachfrage nach neutralen Orientierungstools – wahlkabine.at**

- [Über 500.000 Nutzer:innen](https://wahlkabine.at/downloads/2019%20NRW_Medieninformation.pdf) bei der EU-Wahl 2019, [über eine Million Nutzungen](https://web.de/magazine/politik/wahlen/nationalratswahl/wahlhilfe-nationalratswahl-wahlkabineat-demokratie-helfen-32549706) vor der Nationalratswahl 2013 – bei rund 6,3 Mio. Wahlberechtigten
- [Anfang 2024 aus finanziellen Gründen eingestellt](https://futurezone.at/netzpolitik/wahlkabineat-online-wahlentscheidung-oesterreich/402624881), weil kommerzielle Monetarisierung wegen der Unabhängigkeit ausgeschlossen wurde; erst durch neue Partner (Volkshochschulverband, SOS-Kinderdorf) für die Nationalratswahl 2024 gerettet
- Lehre: Nachfrage ist belegt, aber Neutralität und Finanzierung stehen in Spannung – Partner mit Bildungsauftrag statt Werbung oder parteinahe Geldgeber
- wahlkabine.at zeigt Positionen, nicht Wirkung – es gibt also ein bewährtes Publikum, dem die nächste Stufe fehlt

**Finanzwissen ist nicht das Problem**

Österreich liegt in der [OECD/INFE-Finanzbildungserhebung 2023](https://oenb.at/dam/jcr:4c435dd7-af6d-4496-be74-aaae843d70e6/report-2024-13-financial-literacy-executive-summary-de.pdf) der OeNB im Spitzenfeld von 38 Ländern. Die Hürde ist also nicht fehlendes Rechenverständnis, sondern dass die Wirkung politischer Entscheidungen in WFA, Budgetdienst-Analysen und Gesetzestexten steckt, die nur Fachleute lesen. Das bestätigt den Ansatz: übersetzen und personalisieren, nicht belehren.

**Was die Interviews klären sollen (10–15 Gespräche)**

- Wann hast du zuletzt versucht herauszufinden, was eine Entscheidung konkret für dich bedeutet? Wo hast du gesucht, was hat gefehlt?
- Beispielhaushalt oder „Mein Haushalt": Was liest du zuerst?
- Wie tief willst du klicken können, bevor du der Zahl glaubst?
- Würdest du melden, wenn dich eine Maßnahme anders trifft als dargestellt?
- Von wem müsste die Seite kommen, damit du ihr traust – und von wem auf keinen Fall?

## Projektcanvas

Eine Seite, die später den Kern jedes Förderantrags bildet. Arbeitstitel offen.

| Feld | Inhalt |
| --- | --- |
| **Problem** | Politische Entscheidungen werden positiv kommuniziert; was sie für den eigenen Haushalt bedeuten, steht in WFA, Budgetdienst-Analysen und Gesetzestexten, die nur Fachleute lesen. 65 % finden, das System funktioniere nicht gut; im unteren Einkommensdrittel sehen sich 17 % im Parlament vertreten. |
| **Zielgruppe** | Primär: Menschen im unteren und mittleren Einkommensdrittel, die wissen wollen, was eine Entscheidung für sie heißt. Sekundär: Journalist:innen, Lehrer:innen (politische Bildung), Multiplikator:innen in Sozialorganisationen. |
| **Lösung** | Pro Maßnahme eine Karte in zwei Ebenen: oben in drei Sätzen und Euro pro Jahr für Beispielhaushalte oder den eigenen Haushalt; darunter Detailseiten mit Rechenweg, Annahmen, Quellen (WFA, Budgetdienst, EUROMOD) und Konfidenz-Label. Kurz- und langfristige Wirkung getrennt. |
| **Abgrenzung** | Budgetdienst: rechnet, erklärt aber nicht für Laien. wahlkabine.at / wahl.chat: zeigen Positionen, nicht Wirkung. Momentum Institut / Agenda Austria: interpretieren mit erkennbarer Schlagseite. Wir: nur Wirkung in Euro und Betroffenen, keine Wertung, alle Annahmen offen, Open Source. |
| **Wirkungslogik** | Aktivität: Maßnahmen strukturiert erfassen, mit EUROMOD rechnen, verständlich erklären → Output: öffentliche Karten, Follow-ups nach einem Jahr, Feedback-Daten → Wirkung: Menschen können Kommunikation und Realität vergleichen; Medien und Abgeordnete nutzen die Zahlen; mittelfristig Druck in Richtung verpflichtender Verteilungs-Check. |
| **Neutralitätsgarantien** | Methodenbeirat mit Ökonom:in; Annahmen versioniert im Repo; Label „nicht bezifferbar" statt Schätzung; Finanzierung offengelegt; keine parteinahen Geldgeber; Fehler öffentlich korrigiert. |
| **Ressourcen** | Du: Entwicklung, LLM/RAG, Produkt. Gesucht: Ökonom:in (Beirat), später Redaktionshilfe. Kosten: Hosting 20–60 €/Monat, LLM 50–300 €/Monat, EUROMOD kostenlos; Hauptkosten Arbeitszeit (\~1.300 h für den MVP). |
| **Finanzierung** | Phase 1 unbezahlt nebenberuflich; netidee (bis 60.000 €) und NGI Zero 2027; Jahr 2: Stiftungen, CERV, Medienkooperation, Mitgliedschaften; Verein bei Bedarf. |
| **Risiken** | Neutralitätsangriffe (Antwort: offene Annahmen, Beirat, Korrekturprozess); kein EU-SILC-Zugang (Plan B: Beispielhaushalte bleiben Kernprodukt); EUROMOD deckt Maßnahme nicht ab (ehrlich labeln); Einzelperson brennt aus (Abbruchkriterium definieren); Haftung für Fehler (Disclaimer plus Korrekturprozess, einmal juristisch prüfen); Datenschutz (Haushaltsrechnung lokal im Browser). |
| **Erfolgskriterien nach 12 Monaten** | 15–20 Maßnahmen online; 5.000 Nutzer:innen pro Monat; 200 Betroffenheits-Meldungen; ein Medium hat Zahlen übernommen; Beirat besteht aus mindestens zwei Personen; kein öffentlich unwidersprochener Fehler. |

**Offen bis zum Interview-Ende**

- [ ] Lesen Menschen zuerst Beispielhaushalt oder „Mein Haushalt"? Entscheidet die Startseite.
- [ ] Reichen drei Sätze oben, oder wollen sie eine Zahl? Entscheidet das Kartenformat.
- [ ] Welcher Absender schafft Vertrauen? Entscheidet, ob Uni-Partner vor Launch nötig ist.

## Startdokumente

Fünf Dokumente vor der ersten Codezeile, vier parallel dazu, alle im Repo unter `/docs`. Methodik-Handbuch und Stilguide sind eigene Docs: Methodik-Handbuch v0 und Stilguide und Kartenformat.

| # | Dokument | Zweck | Wo | Vor Code? |
| --- | --- | --- | --- | --- |
| 1 | Methodik-Handbuch v0 | Redaktionsstatut: Auswahl, Quellen, Annahmen, Labels, Freigabe, Korrektur | eigenes Doc → `/docs/methodik.md` | Ja |
| 2 | Stilguide und Kartenformat | Prüfbare Verständlichkeitsregeln, Kartenstruktur, Eval-Kriterien | eigenes Doc → `/docs/stilguide.md` | Ja |
| 3 | Maßnahmen-Schema mit Referenzbeispiel | Datenvertrag zwischen Redaktion und Code (englisch, länderfähig): Vorhaben, Maßnahme, Beispielhaushalte pro Land; Klimabonus komplett befüllt; Prüfung mit `uv run --with pyyaml --with jsonschema schema/validate.py` | `/schema/massnahme.schema.json`, `/data/jurisdictions/AT.yaml`, `/data/households/AT.yaml`, `/data/bills/AT-XXVIII-I-69.yaml`, `/data/measures/at-2025-klimabonus.yaml` | Ja |
| 4 | Arbeitsplan und Gates | Kanban, Wochenbudget, Pausenkriterium | GitHub Projects + unten | Ja |
| 4a | Architektur | Schichten, Komponenten, Datenzugang (Dateien, Exporte, REST, MCP), Identifier, Bundesländer | `/docs/architecture.md` | Ja |
| 5 | Interview-Leitfaden und Raster | 10–15 Gespräche auswertbar machen | unten | Ja |
| 6 | Entscheidungslog | Ein Eintrag pro Entscheidung mit Grund | `/docs/decisions.md` | Läuft |
| 7 | Governance- und Transparenzseite | Wer, wie finanziert, Beirat, Interessenkonflikte, Korrekturkontakt | Entwurf unten → Website | Parallel |
| 8 | Rechtliches Minimum | Lizenz, Impressum, Datenschutz, Disclaimer | `/LICENSE`, `/docs/legal.md` | Parallel |
| 9 | Stakeholder-Liste | Wer, warum, wann ansprechen, Status | private Tabelle | Parallel |

**Arbeitsplan und Gates**

- Wochenbudget 8 Stunden: höchstens 5 Entwicklung, mindestens 2 Redaktion (Maßnahmen, Quellen), 1 Organisation (Kontakte, Anträge, Log). Wenn Code die Redaktion frisst, stimmt die Reihenfolge nicht.
- Ein Kanban mit vier Spalten: Idee · Diese Phase · In Arbeit (max. 3) · Fertig. Die Checklisten aus der Roadmap sind die Startkarten.
- Pausenkriterium: Nach drei Monaten weniger als drei freigegebene Maßnahmen oder kein Beiratskontakt → Scope halbieren (nur Karten, kein „Mein Haushalt") statt weitermachen wie bisher.
- Abbruchkriterium: Zwei Förderabsagen und nach zwölf Monaten unter 500 Nutzer:innen pro Monat → Projekt als Open-Source-Datensatz und Methodik abschließen, nicht als Produkt.
- Rituale: Freitag 30 Minuten Wochenreview (fertig, blockiert, Stundenbudget eingehalten?); erster Montag im Monat 30 Minuten Canvas-Check (welche Annahme hat sich geändert?).

**Interview-Leitfaden (20 Minuten)**

1. Einstieg (3 Min.): Wie informierst du dich, wenn die Regierung etwas beschließt, das dich betreffen könnte? Letztes Beispiel?
2. Problem (5 Min.): Hast du schon mal versucht herauszufinden, was so eine Entscheidung für dich in Euro heißt? Wo hast du gesucht, wo hast du aufgegeben?
3. Karte zeigen (7 Min.): Papier- oder Bildschirmentwurf der Klimabonus-Karte. Lies das. Was ändert sich für wen? (Antwort notieren, nicht korrigieren.) Was liest du zuerst: Beispielhaushalt oder „Mein Haushalt"? Reichen dir die drei Sätze oder willst du eine Zahl zuerst?
4. Vertrauen (3 Min.): Glaubst du der Zahl? Was müsstest du anklicken können, um sie zu glauben? Von wem müsste die Seite kommen – und von wem auf keinen Fall?
5. Mitmachen (2 Min.): Würdest du melden, wenn dich eine Maßnahme anders trifft als dargestellt? Würdest du dich für ein Follow-up in einem Jahr eintragen?

Auswertungsraster, eine Zeile pro Gespräch:

| Haushaltstyp | Bisherige Quelle | Wirkung richtig wiedergegeben? | Zuerst gelesen | Tiefe gewünscht | Vertrauensabsender | Ablehnung | Zitat |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | ja / teilweise / nein | Beispiel / Mein Haushalt / Zahl | Satz / Zahl / Rechenweg |  |  |  |

Muster zählen ab 10 Gesprächen: Wenn 7 von 10 die Wirkung richtig wiedergeben, ist Ebene 1 gut genug. Wenn weniger als 5 der Zahl glauben, kommt der Uni-Partner vor den Launch.

**Entscheidungslog**

Geführt in `docs/decisions.md`, ein Eintrag pro Entscheidung mit Datum, Alternativen, Grund und Revidierbarkeit.

**Governance- und Transparenzseite – Entwurf**

- Wer: Name, Rolle, berufliche Tätigkeit, Parteimitgliedschaften (keine / welche), sonstige Funktionen
- Finanzierung: jede Quelle mit Betrag und Jahr; abgelehnte Geldgeber und warum
- Methodenbeirat: Mitglieder, Rolle (prüft Methodik und Annahmen, nicht Texte), Rechte (Veto bei Methodikänderung), kein Honorar oder welches
- Interessenkonflikte: Verfahren, wenn eine Maßnahme den Autor selbst betrifft (Offenlegung auf der Karte)
- Unabhängigkeit: keine Werbung, keine parteinahe Finanzierung, Zahlen werden nur über den Korrekturprozess geändert
- Korrekturen: Link zur Korrekturseite, Kontakt, Reaktionszeit 7 Tage
- Lizenz und Nachnutzung: Code und Daten offen, Bedingungen

**Rechtliches Minimum – Checkliste**

- [ ] Lizenz gewählt (Code: AGPL-3.0 oder MIT; Inhalte: CC-BY-SA 4.0)
- [ ] Impressum nach § 25 MedienG (Website mit redaktionellem Inhalt)
- [ ] Datenschutzerklärung; „Mein Haushalt" rechnet lokal, keine Speicherung – dokumentieren
- [ ] Disclaimer: keine Rechts-, Steuer- oder Finanzberatung; Zahlen sind Modellrechnungen
- [ ] Einmal von einer Jurist:in gegenlesen lassen (Haftung für fehlerhafte Zahlen, Zitatrecht für Element 3)

## Roadmap

Jetzt klein bauen, groß erst mit Förderung: Alles vor der Fördervereinbarung zählt nicht als Kosten, aber als Beweis, dass du es kannst. Der Prototyp sichert den Antrag, der geförderte Zeitraum (ca. 1.300 Stunden) baut den MVP und bringt ihn zu Nutzer:innen. Annahme bis zur Förderung: 8–10 Stunden pro Woche nebenberuflich.

Reihenfolge nach Datenzugang: zuerst, was strukturiert und frei verfügbar ist (Parlaments-API, WFA, Budgetdienst), dann die eigene Rechnung (EUROMOD), danach Abstimmungsverhalten, zuletzt Wahlprogramme. Kein Gate hängt an EUROMOD, bis die Karten ohne eigene Rechnung bei Nutzer:innen funktionieren. Eine Wahlhilfe kommt erst zur Nationalratswahl 2029 und baut auf beschlossenen Maßnahmen und Abstimmungsverhalten auf, nicht auf Versprechen.

| Phase | Zeitraum | Ziel (Gate) |
| --- | --- | --- |
| 0 Fundament | Nov–Dez 2026 | Alle Gesetzesvorhaben des Bundes 2025/2026 als Bill-Records aus der Ingestion (Postgres raw und staged); fünf Karten aus dem Konsolidierungspaket 2025 händisch erstellt, nur Labels „Übernommen" und „nicht bezifferbar"; Interviews laufen |
| 1 Prototyp | Jan–Mär 2027 | Öffentliche Seite mit fünf Karten und Gesetzes-Tracker (Status, nächster Schritt); EUROMOD rechnet einen Beispielhaushalt; Ökonom:in zugesagt |
| 2 Anträge | Feb–Jun 2027 | NGI-Zero-Antrag eingereicht (Feb), netidee-Antrag eingereicht (Frist Frühsommer) |
| 3 Warten, nicht stillstehen | Jul–Okt 2027 | Monatlich eine neue Maßnahme, erste Karten mit Label „Gerechnet", Feedback aus Soft-Launch, Uni-Kontakt für EU-SILC |
| 4 Geförderter Bau | Nov 2027–Apr 2028 | MVP mit „Mein Haushalt", Fragen-Chat, Feedback-Features, Abstimmungsverhalten pro Fraktion; öffentlicher Launch |
| 5 Ausbau | ab Mai 2028 | Echte Dezile mit EU-SILC, Follow-ups, Verein, Stiftungen, Medienkooperation; Wahlbilanz und Wahlprogramme zur Nationalratswahl 2029 |

**Phase 0 – Fundament (Nov–Dez 2026)**

Ziel ist der Nachweis, dass die Karte ohne eigenes Modell funktioniert. Alles händisch, kein LLM, kein EUROMOD im Gate.

- [ ] Öffentliches Repo anlegen (OSI-Lizenz, z. B. AGPL oder MIT; Inhalte CC-BY-SA) – netidee verlangt das später ohnehin, und das Datum des ersten Commits ist dein Beleg für Eigeninitiative
- [ ] Konsolidierungspaket 2025 als erstes Quellencluster: Klimabonus-Abschaffung, höherer Krankenversicherungsbeitrag für Pensionist:innen, ausgesetzte Valorisierungen. Alle Maßnahmen haben Regierungsvorlage, WFA und eine Budgetdienst-Analyse mit Dezilen
- [ ] Parlaments-API anbinden (JSON, CC BY 4.0, Detailseiten mit `?json=TRUE`): alle Verhandlungsgegenstände der XXVIII. GP in die Postgres-Schicht `raw` laden, Detail-JSON für Regierungsvorlagen, Initiativanträge und Beschlüsse; Transformation nach `staged`; Export aller Gesetzesvorhaben 2025/2026 als Bill-Records nach `data/bills/`; Materialien-PDFs (WFA) über die verlinkten Dokumente holen
- [ ] Maßnahmen-Schema v0 aus den tatsächlichen Feldern der API ableiten, nicht aus dem Konzept; dazu Quellenangaben mit URL und Seitenzahl, Annahmen-Block, Konfidenz-Label
- [ ] Fünf Karten händisch schreiben: Element 5 nur mit „Übernommen" (Budgetdienst-Dezile, WFA-Angaben) oder reiner Arithmetik aus dem Gesetz bei Pauschalbeträgen (Klimabonus 290 € → 0 €), sonst „nicht bezifferbar". Der Budgetdienst liefert Prozent pro Dezil, keine Euro pro Haushaltstyp – das wird auf der Karte so benannt
- [ ] Interviews mit diesen Karten führen (Leitfaden oben); das Ergebnis entscheidet, ob eine Zahl vor den drei Sätzen steht und wie viel Priorität EUROMOD in Phase 1 bekommt
- [ ] EUROMOD registrieren und installieren (JRC-Download v3.8.6, Modell AT, Python-Paket `euromod`), HHoT mit einem Haushalt ausprobieren – parallel, kein Gate
- [ ] Zwei bis drei Ökonom:innen anschreiben (Dissertant:innen Verteilungsökonomie WU/JKU/Uni Graz; Autor:innen der Budgetdienst-Analysen als Hinweis, wer im Thema ist)
- [ ] Call-22-Termine bei netidee abonnieren (Newsletter), Infoabend-Termin notieren
- [ ] KESt-Frage an antrag@netidee.at stellen; Steuerberater nach Privatperson vs. Einzelunternehmen fragen

**Phase 1 – Prototyp (Jan–Mär 2027)**

Ziel ist ein Beweis, kein Produkt: Alles statisch vorgeneriert, kein Login, kein freier Chat. Erst jetzt kommen LLM und EUROMOD dazu, weil nach fünf händischen Karten klar ist, was „gut" heißt.

- [ ] Gesetzes-Tracker als Rückgrat der Ingestion: pro Verhandlungsgegenstand Status (Begutachtung, Regierungsvorlage, Ausschuss, Plenum, Bundesrat, Bundesgesetzblatt), nächster Schritt und Termine aus der API; wird Element 2 der Karte und als eigene Ansicht „Wo steht das Gesetz gerade" gezeigt – kein zweites Produkt, sondern die Pipeline, die ohnehin nötig ist
- [ ] Ingestion-Pipeline: Regierungsvorlagen, WFA und Budgetdienst-Analysen laden, PDF-Extraktion, Chunking, Vektorindex – dein RAG-Standardfall
- [ ] LLM-Schritt „Maßnahmen-Entwurf": aus den Quellen den Schema-Entwurf erzeugen, immer mit Zitatstellen; Mensch gibt frei (Review-Datei im Repo); die fünf händischen Karten sind der Maßstab
- [ ] LLM-Schritt „Erklärung": aus freigegebenem Objekt und Zahlen die Sieben-Elemente-Karte texten; Stilregeln als Prompt-Datei im Repo (keine Wertung, Zahlen immer mit Label)
- [ ] EUROMOD als Tool kapseln: kleiner Service (MCP-Server oder REST), Input = Haushalt + Parameteränderung, Output = verfügbares Einkommen vorher/nachher; sechs Beispielhaushalte als HHoT-Inputdateien; Ergebnisse cachen und im Repo versionieren. Label „Gerechnet" nur für Maßnahmen, die Tarif oder Zusammenspiel von Abgaben und Transfers ändern; Pauschalbeträge bleiben Arithmetik
- [ ] Statische Website (z. B. Astro/Next static export) mit den fünf Karten, Beispielhaushalt-Umschalter, Tracker-Status, Methodenseite mit allen Annahmen
- [ ] Eval-Set von Anfang an: 30–50 Fragen mit erwarteten Antworten oder „nicht beantwortbar"; läuft bei jeder Prompt-Änderung
- [ ] Feedback minimal: „Trifft mich das?" plus Freitext, zunächst als GitHub Issues oder einfaches Formular
- [ ] Soft-Launch im kleinen Kreis (Bekannte, ein Posting auf LinkedIn/Mastodon), 20 Rückmeldungen einsammeln

**Phase 2 – Anträge (Feb–Jun 2027)**

- [ ] NGI Zero (NLnet): Antrag für den Baustein „offener EUROMOD-Tool-Server für LLM-Agenten" – Calls etwa alle zwei Monate, Antrag wenige Seiten, Einreichung Februar
- [ ] netidee Call 22: Antrag mit Arbeitspaketen für 18 Monate, Video mit laufendem Prototyp, Verwertungsplan (Verein, Uni-Partner, Medienkooperation), Beirat namentlich
- [ ] Arbeitspakete grob: AP1 Datenpipeline, Gesetzes-Tracker und Maßnahmen-Redaktion · AP2 EUROMOD-Integration und Beispielhaushalte · AP3 „Mein Haushalt" · AP4 Fragen-Chat mit Quellenbindung · AP5 Feedback, Follow-up und Abstimmungsverhalten · AP6 Methodik, Beirat, Dokumentation · AP7 Launch und Community
- [ ] Vor Einreichung: Entwurf von zwei Außenstehenden lesen lassen, eine:r davon technisch, eine:r nicht

**Phase 3 – Warten, nicht stillstehen (Jul–Okt 2027)**

- [ ] Monatlich eine neue Maßnahme; im Oktober kommt die Budgetrede – das Budgetbegleitgesetz liefert viele Maßnahmen auf einmal
- [ ] Erste Karten mit Label „Gerechnet": Maßnahmen mit Tarifänderung über EUROMOD rechnen, Abweichung zu Budgetdienst-Zahlen auf der Detailseite benennen
- [ ] Uni-Partner konkretisieren und EU-SILC-Zugang über das Institut beantragen
- [ ] Erste Journalist:in kontaktieren (Standard, Falter), Prototyp zeigen, Interesse an Kooperation abfragen
- [ ] Bei Absage von netidee: NGI-Zero-Ergebnis abwarten, CERV-Partner suchen, Phase 4 verkleinert nebenberuflich weiterführen

**Phase 4 – Geförderter Bau (Nov 2027–Apr 2028)**

- [ ] „Mein Haushalt": Eingabe lokal im Browser, Rechnung gegen vorgenerierte EUROMOD-Raster oder Live-Service
- [ ] Fragen-Chat: nur aus hinterlegten Quellen, Rate-Limit, kleines Modell, Cache; unbeantwortete Fragen in Recherche-Liste
- [ ] Abstimmungsverhalten pro Fraktion: die Parlaments-API liefert das Ergebnis der dritten Lesung pro Fraktion strukturiert (Feld `vote` im Detail-JSON, siehe API-Spike); keine Extraktion aus Protokollen nötig; auf der Detailseite als „Wer hat dafür gestimmt" nüchtern gelistet
- [ ] Fehler-Flags mit öffentlicher Issue-Liste, Follow-up-Daten pro Maßnahme mit Erinnerung
- [ ] Blog alle drei Monate auf netidee.at (Pflicht) – gleichzeitig dein Launch-Kanal
- [ ] Öffentlicher Launch mit 15–20 Maßnahmen, idealerweise mit Medienpartner

**Phase 5 – Ausbau (ab Mai 2028)**

- [ ] Echte Dezile mit EU-SILC
- [ ] Verein gründen, Mitgliedermodell, Stiftungen und CERV mit Nutzerzahlen ansprechen
- [ ] Wahlbilanz zur Nationalratswahl 2029: beschlossene Maßnahmen, gemessene Wirkung und Abstimmungsverhalten pro Fraktion als neutrale Wahlhilfe – Bilanz statt Versprechen, kein eigener Positionsvergleich (das decken wahlkabine.at und wahl.chat ab)
- [ ] Wahlprogramme erst danach, mit ergänzter Methodik (Übersetzung von Absichten in Parameter, Beirat zeichnet gegen)

**Diese Woche:** Repo anlegen, Parlaments-API für das Konsolidierungspaket 2025 abfragen, Schema v0 aus den Feldern ableiten, Klimabonus-Abschaffung als erste Karte händisch schreiben, EUROMOD-Registrierung nebenbei starten.
