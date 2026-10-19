# Methodik-Handbuch v0

Oct 19, 2026 · @Valcome Innovation GmbH

Dieses Handbuch legt fest, wie eine politische Maßnahme ausgewählt, belegt, gerechnet und veröffentlicht wird. Es ist öffentlich, versioniert und gilt für jede Maßnahmen-Karte.

## 1. Zweck und Geltung

Das Handbuch gilt für alle veröffentlichten Inhalte: Maßnahmen-Karten, Detailseiten, Follow-ups und Antworten des Fragen-Chats. Änderungen am Handbuch werden versioniert (Datum, Änderung, Begründung) und nur mit Zustimmung des Methodenbeirats vorgenommen, sobald es ihn gibt. Bis dahin gilt: jede Änderung wird im Entscheidungslog begründet.

Leitprinzip: Wir beschreiben Wirkung in Euro und Betroffenen. Wir bewerten nicht, ob eine Maßnahme gut oder schlecht ist.

## 2. Auswahl der Maßnahmen

Aufgenommen wird eine Maßnahme, wenn alle drei Kriterien erfüllt sind:

1. **Status:** Als Regierungsvorlage oder als Initiativantrag von Abgeordneten der Regierungsfraktionen im Nationalrat eingebracht, beschlossen oder in Kraft. Initiativanträge sind gleichwertig, weil Konsolidierungspakete regelmäßig so eingebracht werden (Beispiel: Budgetsanierungsmaßnahmengesetz 2025, 73/A). Reine Ankündigungen (Pressekonferenz, Interview) werden nur als „angekündigt" erfasst und nicht gerechnet.
2. **Haushaltsbezug:** Verändert Einkommen, Abgaben, Transfers oder Pflichtausgaben privater Haushalte direkt (Steuern, Beihilfen, Pensionen, Gebühren, Mindestlohn, Valorisierungen).
3. **Belegbarkeit:** Mindestens eine Primärquelle (Gesetzestext oder WFA) ist öffentlich zugänglich. Bei Initiativanträgen gibt es keine WFA und keine Begutachtung; Beleg sind dann Gesetzestext und Budgetdienst-Analyse. Die Karte kennzeichnet das Fehlen der WFA in Element 6 („Was ist unklar").

Nicht aufgenommen: Maßnahmen ohne direkten Haushaltsbezug (Verwaltungsreform, Außenpolitik), Landes- und Gemeindeentscheidungen (vorerst), Maßnahmen, deren Wirkung nur über Makro-Effekte läuft (Konjunkturpakete, Standortpolitik).

Reihenfolge bei knapper Zeit: zuerst nach Zahl der Betroffenen, dann nach Euro-Wirkung pro Haushalt. Die Auswahlentscheidung wird pro Maßnahme mit einem Satz festgehalten, auch die Ablehnung.

## 3. Quellen

Jede Zahl und jede Aussage über den Inhalt einer Maßnahme trägt eine Quelle mit URL und Seiten- oder Paragrafenangabe. Keine Quelle, keine Veröffentlichung.

| Rang | Quelle | Rolle im Schema | Verwendung |
| --- | --- | --- | --- |
| 1 | Gesetzestext, Regierungsvorlage, Bundesgesetzblatt (RIS, parlament.gv.at) | `law_text` | Was gilt – maßgeblich bei jedem Widerspruch |
| 2 | Wirkungsorientierte Folgenabschätzung (WFA) | `impact_assessment` | Offizielle Kosten- und Betroffenenschätzung der Regierung; fehlt bei Initiativanträgen |
| 3 | Budgetdienst des Parlaments | `parliamentary_budget_office` | Unabhängige Prüfung, Verteilungsangaben |
| 4 | Statistik Austria, EU-SILC, OeNB | `statistics` | Haushaltsstruktur, Einkommen, Preise |
| 5 | Wissenschaftliche Studien (WIFO, IHS, Universitäten) | `study` | Ergänzend, mit Nennung des Auftraggebers |
| 6 | Offizielle Pressetexte der Regierung, Budgetrede |  `government_communication` | Nur für den Teil „Was wurde gesagt", nie als Beleg für Wirkung |
| – | Parteinahe Thinktanks, Medienberichte, Social Media | keine | Nicht als Beleg; allenfalls als Hinweis auf eine zu prüfende Frage |

Die Rangfolge ist österreichspezifisch; das Schema kennt nur die Rolle, jedes Land ordnet seine Institutionen den Rollen zu. Bei Widerspruch zwischen Quellen gilt der höhere Rang; der Widerspruch wird auf der Detailseite benannt. Quellen werden mit Abrufdatum archiviert (lokale Kopie im Repo oder Web-Archive-Link), damit spätere Änderungen nachvollziehbar bleiben.

## 4. Operationalisierung

Eine Maßnahme wird in konkrete Parameteränderungen übersetzt (z. B. „Klimabonus: 290 € → 0 € ab 2025, alle Anspruchsberechtigten"). Jede Übersetzung folgt drei Regeln:

1. **Gesetzestext vor Absicht.** Gerechnet wird, was im Gesetz steht, nicht, was die Regierung damit erreichen will.
2. **Jede Lücke ist eine dokumentierte Annahme.** Fehlt eine Angabe (Valorisierung, Übergangsfrist, Anspruchsgrenze), wird die konservativste Lesart gewählt und als Annahme gekennzeichnet: Was wurde angenommen, warum, was würde sich bei anderer Lesart ändern.
3. **Keine Verhaltensanpassung.** Statisch gerechnet: Menschen ändern ihr Verhalten in der Rechnung nicht (kein Mehrarbeiten, kein Ausweichen). Das wird auf jeder Detailseite gesagt.

Das LLM erstellt den Entwurf der Parameterliste mit Zitatstellen; die Freigabe (Abschnitt 7) prüft jede Zeile gegen die Quelle. Eine Maßnahme, deren Parameter sich nicht eindeutig festlegen lassen, erhält das Label „nicht bezifferbar" und eine qualitative Karte ohne Euro-Werte.

## 5. Rechnung

Gerechnet wird mit EUROMOD (Modell Österreich, jeweils aktuellste Version) und dem Hypothetical Household Tool. Ergebnisgröße ist das verfügbare Haushaltseinkommen pro Jahr vor und nach der Maßnahme, zusätzlich pro Monat.

**Beispielhaushalte (v0, anpassbar nach Interviews)**

| Kürzel | Haushalt | Bruttoeinkommen | Wohnsituation |
| --- | --- | --- | --- |
| H1 | Alleinerziehende, 1 Kind (6 J.), Teilzeit 30 h | 2.100 €/Monat | Miete, Wien |
| H2 | Pensionistin, allein, Ausgleichszulage | ca. 1.270 €/Monat | Miete, Landgemeinde |
| H3 | Paar, 2 Kinder (4 und 9 J.), beide Vollzeit | 3.200 € + 2.600 €/Monat | Eigentum mit Kredit, Stadtrand |
| H4 | Student, Nebenjob geringfügig, eigene Wohnung | 550 €/Monat + Familienbeihilfe | WG, Graz |
| H5 | Selbstständiger, allein, Einzelunternehmer | 45.000 €/Jahr Gewinn | Miete, Linz |
| H6 | Paar ohne Kinder, ein Einkommen, Industriearbeiter | 3.400 €/Monat | Eigentum abbezahlt, Land |
| H7 | Paar, 1 Kind, hohe Einkommen | 7.500 € + 5.000 €/Monat | Eigentum, Wien |

Die Haushalte decken bewusst unten, Mitte und oben ab, damit kein Vorwurf entsteht, nur eine Gruppe zu zeigen. Alle Parameter der Haushalte sind im Repo hinterlegt.

**Kurz- und langfristig**

- Kurzfristig: Wirkung im ersten vollen Jahr nach Inkrafttreten.
- Langfristig: Wirkung im fünften Jahr unter der Annahme, dass alles andere gleich bleibt, einschließlich fehlender Valorisierung, auslaufender Befristungen und Übergangsfristen. Inflationsannahme: aktuelle OeNB-Prognose, auf der Detailseite genannt.
- Keine Makro-Effekte, keine Verhaltensreaktionen, keine Prognose politischer Folgeentscheidungen.

Sobald EU-SILC-Zugang besteht, kommen Dezile dazu; die Beispielhaushalte bleiben die Hauptdarstellung.

## 6. Konfidenz-Labels

Jede Zahl trägt genau ein Label. Das Label steht direkt neben der Zahl, auch in der Kurzfassung.

| Label | Bedeutung | Voraussetzung |
| --- | --- | --- |
| **Gerechnet** | Mit EUROMOD aus den Gesetzesparametern berechnet | Parameter eindeutig, Rechnung reproduzierbar im Repo |
| **Übernommen** | Zahl stammt aus WFA oder Budgetdienst, von uns nicht nachgerechnet | Quelle mit Seitenangabe; Abweichung zu eigener Rechnung, falls vorhanden, genannt |
| **Geschätzt** | Eigene Rechnung mit mindestens einer wesentlichen Annahme | Annahme und Spannweite (niedrig/hoch) auf der Detailseite |
| **Nicht bezifferbar** | Keine belastbare Zahl möglich | Begründung in einem Satz; Karte nur qualitativ |

„Geschätzt" wird sparsam vergeben; im Zweifel „nicht bezifferbar". Ein Label wird nie hochgestuft, um eine Karte attraktiver zu machen.

## 7. Freigabe

Keine Karte geht ohne menschliche Freigabe online. Die Freigabe ist eine Checkliste im Repo (Pull Request), die pro Maßnahme abgehakt und archiviert wird.

- [ ] Jede Parameterzeile gegen die Primärquelle geprüft (Seite/Paragraf notiert)
- [ ] Alle Annahmen dokumentiert, konservativste Lesart gewählt
- [ ] Rechnung im Repo reproduzierbar (EUROMOD-Version, Inputdateien, Output)
- [ ] Labels korrekt vergeben
- [ ] Text nach Stilguide geprüft (Eval-Set bestanden)
- [ ] Teil „Was wurde gesagt" wörtlich oder sinngemäß mit Quelle belegt
- [ ] Teil „Was ist unklar" nicht leer, oder begründet leer

Solange du allein bist: Freigabe frühestens 24 Stunden nach Erstellung, in einer zweiten Sitzung – das ersetzt notdürftig das zweite Augenpaar. Sobald der Beirat besteht: Jede Maßnahme mit Label „Geschätzt" und jede Maßnahme mit mehr als 500 € Jahreswirkung für einen Beispielhaushalt wird vor Veröffentlichung von einem Beiratsmitglied gegengelesen.

## 8. Korrekturprozess

Fehler werden öffentlich korrigiert, nie still.

1. **Meldung:** Jede Zahl hat einen Melde-Link. Meldung landet als öffentliches Issue (anonym möglich). Eingangsbestätigung automatisch.
2. **Prüfung:** Innerhalb von 7 Tagen wird geprüft und das Ergebnis im Issue begründet: bestätigt, abgelehnt oder offen (mit Grund).
3. **Korrektur:** Bestätigte Fehler werden in der Karte geändert; die alte Version bleibt in der Versionsgeschichte sichtbar. Die Karte trägt eine Änderungsnotiz mit Datum und einem Satz.
4. **Wesentliche Fehler** (Vorzeichen falsch, Betroffenengruppe falsch, Wirkung um mehr als 20 % daneben) werden zusätzlich auf einer Korrekturseite gelistet und, wenn die Zahl von Medien übernommen wurde, aktiv an diese gemeldet.

Meldungen, die keine Fehler, sondern Meinungsunterschiede betreffen („das ist unfair"), werden freundlich mit Verweis auf Abschnitt 9 beantwortet und geschlossen.

## 9. Was wir nicht tun

- Keine Bewertung: kein „gerecht", „unfair", „sinnvoll", „verfehlt"
- Keine Prognosen über Wirtschaftswachstum, Beschäftigung oder Verhalten
- Keine Parteivergleiche ohne durchgerechnete Grundlage; Wahlprogramme erst, wenn die Methodik dafür ergänzt ist
- Keine Personalisierung über das Nötige hinaus: „Mein Haushalt" rechnet lokal, wir speichern keine Eingaben
- Keine Empfehlungen, wie man wählen oder sich verhalten soll
- Keine Zahl ohne Label, keine Aussage ohne Quelle
- Keine Annahme parteinaher oder anonymer Finanzierung; alle Geldgeber werden veröffentlicht
- Keine Reaktion auf politischen Druck durch Änderung von Zahlen – nur durch den Korrekturprozess
