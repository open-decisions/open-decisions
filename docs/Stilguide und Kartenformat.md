# Stilguide und Kartenformat

Oct 19, 2026 · @Valcome Innovation GmbH

Der Stilguide macht aus „für Laien verständlich“ prüfbare Regeln. Er ist zugleich System-Prompt für die Textgenerierung und Maßstab für das Eval-Set.

## 1. Grundsatz: zwei Ebenen

Oben steht, was eine Person ohne Vorwissen in 30 Sekunden versteht. Unten steht alles, was eine Ökonomin braucht, um die Zahl nachzurechnen. Nichts aus der unteren Ebene darf die obere verkomplizieren; nichts aus der oberen Ebene darf ohne Beleg unten stehen.

- Ebene 1 (Karte): drei Sätze, eine Zahl pro Haushalt, ein Label, ein Link „Wie gerechnet?"
- Ebene 2 (Detailseite): Parameter, Annahmen, Rechenweg, Quellen mit Seitenangabe, Spannweiten, offene Fragen
- Test: Eine Person liest nur Ebene 1 und kann in einem Satz sagen, was sich für wen ändert. Eine Fachperson liest nur Ebene 2 und findet keine Lücke.

## 2. Pflichtstruktur der Karte

Jede Karte hat dieselben sieben Elemente in derselben Reihenfolge. Kein Element wird weggelassen; ein leeres Element wird als „Dazu gibt es keine belastbare Angabe" ausgewiesen.

| # | Element | Inhalt | Länge |
| --- | --- | --- | --- |
| 1 | Titel | Was sich ändert, in Alltagssprache | max. 8 Wörter |
| 2 | Status und Datum | angekündigt / beschlossen / in Kraft seit | 1 Zeile |
| 3 | Was wurde gesagt | Offizielle Botschaft, als Zitat mit Quelle | 1–2 Sätze |
| 4 | Was steht im Gesetz | Die Änderung in Parametern, ohne Fachbegriffe | 2–3 Sätze |
| 5 | Was heißt das für dich | Tabelle Beispielhaushalte: Euro/Jahr kurzfristig, Euro/Jahr im 5. Jahr, Label; Umschalter auf „Mein Haushalt" | Tabelle |
| 6 | Was ist unklar | Annahmen, Lücken, Widersprüche zwischen Quellen | 1–3 Punkte |
| 7 | Nachschauen | Link Detailseite, Link Quellen, Melde-Link, Follow-up-Datum | 1 Zeile |

Zwischen Element 3 und 4 steht nie ein Kommentar. Die Lücke zwischen Botschaft und Gesetz zeigt sich durch das Nebeneinander, nicht durch unseren Text.

## 3. Sprache

Zielniveau: verständlich für jemanden, der Boulevardzeitung liest und nie ein Gesetz aufgeschlagen hat. Das ist eine Anforderung an uns, nicht an die Leser:innen.

**Regeln**

- Sätze unter 20 Wörtern, ein Gedanke pro Satz, Aktiv statt Passiv
- Du-Ansprache in Element 5 („für dich"), sonst neutral
- Jeder Fachbegriff wird beim ersten Vorkommen in Klammern erklärt oder ersetzt: „Valorisierung" → „Anpassung an die Inflation"
- Zahlen immer mit Bezugsgröße: „290 € im Jahr, etwa 24 € im Monat"
- Zeitangaben konkret: „ab Jänner 2026", nicht „künftig"
- Keine Ironie, keine rhetorischen Fragen, keine Ausrufezeichen
- Parteien und Personen werden nur in Element 3 (Zitat) genannt, sonst „die Regierung" oder „der Nationalrat"

**Verbotene Wörter** (außer in wörtlichen Zitaten in Element 3)

Entlastung, Belastung, Reform, Paket, gerecht, fair, sinnvoll, notwendig, großzügig, hart, Sparpaket, Geschenk, Kürzung (stattdessen: „wird gestrichen", „sinkt um"), Erhöhung (stattdessen: „steigt um"), Betroffene werden „geschont"/„getroffen".

**Erlaubte Formulierungen für Wirkung**

„bekommt … mehr/weniger", „zahlt … mehr/weniger", „ändert sich nicht", „hängt davon ab, ob …", „dazu gibt es keine belastbare Angabe".

## 4. Zahlen

- Einheit: Euro pro Jahr, daneben pro Monat in Klammern; Vorzeichen immer ausgeschrieben („minus 290 €", nicht „–290 €")
- Rundung in Ebene 1: auf 10 € bei Beträgen unter 1.000 €, auf 50 € darüber; in Ebene 2 ungerundet
- Zwei Zeitpunkte, immer beide: erstes volles Jahr und fünftes Jahr
- Vergleichsgröße bei jeder Zahl über 500 €: Anteil am verfügbaren Jahreseinkommen des Beispielhaushalts („rund 1,5 % des Einkommens")
- Spannweiten statt Scheingenauigkeit bei Label „Geschätzt": „zwischen 180 und 240 €"
- Label steht direkt hinter der Zahl, als Wort, nicht als Symbol: „290 € (gerechnet)"
- Null ist eine Zahl: „ändert sich nicht (gerechnet)" steht auf jeder Karte für die Haushalte, die nicht betroffen sind
- Keine Prozentangaben ohne Basis, keine kumulierten Summen über mehrere Jahre in Ebene 1

## 5. Detailseite

Die Detailseite ist für Fachleute und für misstrauische Laien. Sie ist vollständig, aber in fester Reihenfolge, damit man gezielt springen kann.

1. **Parameter:** Tabelle alt → neu, mit Paragraf und Quelle pro Zeile
2. **Annahmen:** nummeriert; pro Annahme: Was, Warum, Was wäre anders bei anderer Lesart
3. **Rechenweg:** EUROMOD-Version, Haushaltsdefinitionen, Link zu Inputdateien und Output im Repo; bei „Übernommen" die Seite der Quelle und ggf. die Abweichung zur eigenen Rechnung
4. **Spannweiten:** bei „Geschätzt" niedrige und hohe Variante mit Begründung
5. **Quellen:** vollständige Liste mit Abrufdatum und Archivlink
6. **Widersprüche:** zwischen Quellen oder zwischen Botschaft und Gesetz, nüchtern nebeneinandergestellt
7. **Offene Fragen:** was wir nicht wissen und wen wir gefragt haben
8. **Änderungsverlauf:** Datum, Änderung, Grund

Auf der Detailseite dürfen Fachbegriffe stehen, aber jeder bekommt beim ersten Vorkommen einen Tooltip oder eine Klammer. Die Sprachregeln aus Abschnitt 3 (keine Wertung, keine verbotenen Wörter) gelten auch hier.

## 6. Prüfliste und Eval

Vor jeder Veröffentlichung, von Hand:

- [ ] Alle sieben Elemente vorhanden, in der richtigen Reihenfolge
- [ ] Kein verbotenes Wort außerhalb von Zitaten
- [ ] Jede Zahl mit Einheit, Zeitpunkt und Label
- [ ] Jeder Haushalt hat einen Wert, auch „ändert sich nicht"
- [ ] Element 6 ist nicht leer oder begründet leer
- [ ] Eine fachfremde Person hat Ebene 1 gelesen und die Wirkung in einem Satz richtig wiedergegeben

Automatisch, bei jeder Prompt- oder Modelländerung (Eval-Set, 30–50 Fälle):

| Prüfung | Methode | Schwelle |
| --- | --- | --- |
| Verbotene Wörter | Regex gegen Liste, Zitate ausgenommen | 0 Treffer |
| Satzlänge | Durchschnitt und Maximum pro Element | Ø < 15, max. 20 Wörter |
| Zahlentreue | Jede Zahl im Text muss im Maßnahmen-Objekt vorkommen | 100 % |
| Quellentreue | Jede Aussage in Element 3 und 4 hat einen Zitatanker | 100 % |
| Label vorhanden | Jede Zahl trägt ein Label | 100 % |
| Lesbarkeit | Flesch-Index für Deutsch (Amstad) auf Ebene 1 | > 60 |
| Wertungsfreiheit | LLM-Judge mit Rubrik „enthält Bewertung ja/nein", stichprobenartig von Hand geprüft | 0 Treffer |
| Verweigerung | Fragen außerhalb der Quellen werden mit „dazu haben wir keine Angabe" beantwortet | 100 % |
