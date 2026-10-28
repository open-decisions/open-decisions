import re
from collections.abc import Iterable
from typing import Any

SECTION = re.compile(r"Verhältnis zu den Rechtsvorschriften der Europäischen Union\s+(.{0,600})", re.S)
SECTION_END = re.compile(r"Besonderheiten|www\.parlament|Wirkungsorientierte|WFA gesamt")
STATEMENT_KINDS = [
    (re.compile(r"fallen nicht in den Anwendungsbereich"), "national"),
    (re.compile(r"geht über eine verpflichtende Umsetzung"), "goes_beyond"),
    (re.compile(r"flankierenden? Regelungen? zu(r)? Verordnung"), "implements_regulation"),
    (re.compile(r"Umsetzung|umgesetzt"), "transposes_directive"),
    (re.compile(r"fallen in den Anwendungsbereich|im Einklang mit|nicht entgegen|zu berücksichtigen"), "eu_scope"),
]
PRIORITY = ["transposes_directive", "implements_regulation", "eu_scope", "national"]

DIRECTIVE = re.compile(r"Richtlinien?\s+(?:\((?:EU|EG|EWG)\)\s*)?(?:Nr\.\s*)?(\d{2,4})/(\d{1,4})(?:/(?:EU|EG|EWG))?")
REGULATION = re.compile(r"(?:Durchführungs|Delegierte[nr]?\s)?[Vv]erordnung\s+\((EU|EG|EWG|Euratom)\)\s*(Nr\.\s*)?(\d{1,4})/(\d{2,4})")
CELEX = re.compile(r"CELEX[- ]?Nr\.?:?\s*(3\d{4}[LR]\d{4})")
TRANSPOSE_CTX = re.compile(r"(umsetzung|umgesetzt|umzusetzen)", re.I)
IMPLEMENT_CTX = re.compile(r"(durchführung|flankierend|begleit|anpassung an)", re.I)


def _year(y: str) -> int:
    n = int(y)
    if n < 100:
        return 1900 + n if n >= 50 else 2000 + n
    return n


def celex(kind: str, year: int, number: int) -> str:
    return f"3{year:04d}{kind}{number:04d}"


def act(celex_id: str, role: str) -> dict[str, Any]:
    year, kind, number = int(celex_id[1:5]), celex_id[5], int(celex_id[6:])
    eli_type = "dir" if kind == "L" else "reg"
    return {
        "celex": celex_id,
        "type": "directive" if kind == "L" else "regulation",
        "label": f"{'Richtlinie' if kind == 'L' else 'Verordnung'} {year}/{number}",
        "role": role,
        "eurlex_url": f"https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX:{celex_id}",
        "eli": f"http://data.europa.eu/eli/{eli_type}/{year}/{number}/oj",
    }


def directive_celex(m: re.Match[str]) -> str | None:
    a, b = m.group(1), m.group(2)
    if len(a) == 4 and 1950 <= int(a) <= 2100:
        year, number = int(a), int(b)
    elif len(a) == 2:
        year, number = _year(a), int(b)
    else:
        return None
    return celex("L", year, number)


def regulation_celex(m: re.Match[str]) -> str | None:
    has_nr, a, b = m.group(2), m.group(3), m.group(4)
    if has_nr or (len(b) == 4 and len(a) <= 4 and int(b) >= 1950 and not (len(a) == 4 and int(a) >= 2015)):
        number, year = int(a), _year(b)
    else:
        year, number = _year(a), int(b)
    if not 1950 <= year <= 2100:
        return None
    return celex("R", year, number)


def statements(text: str, url: str) -> list[dict[str, Any]]:
    out = []
    pages = text.split("\f")
    for page_no, page in enumerate(pages, 1):
        for m in SECTION.finditer(page):
            s = re.sub(r"\s+", " ", m.group(1))
            s = SECTION_END.split(s)[0].strip()
            if not s:
                continue
            kinds = [k for rx, k in STATEMENT_KINDS if rx.search(s)]
            kind = "goes_beyond" if "goes_beyond" in kinds else (kinds[0] if kinds else "eu_scope")
            out.append({"text": s[:300], "kind": kind, "source": url, "page": page_no if len(pages) > 1 else None})
    return out


def acts(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = [(m.group(1), "transposed") for m in CELEX.finditer(text)]
    for m in DIRECTIVE.finditer(text):
        window = text[max(0, m.start() - 120) : m.start()]
        if TRANSPOSE_CTX.search(window) and (cid := directive_celex(m)):
            found.append((cid, "transposed"))
    for m in REGULATION.finditer(text):
        window = text[max(0, m.start() - 120) : m.start()]
        if IMPLEMENT_CTX.search(window) and (cid := regulation_celex(m)):
            found.append((cid, "implemented"))
    return found


def relation(documents: Iterable[tuple[str, str]]) -> dict[str, Any]:
    stmts: list[dict[str, Any]] = []
    found: dict[str, str] = {}
    for url, text in documents:
        stmts += statements(text, url)
        for cid, role in acts(text):
            found.setdefault(cid, role)
    seen, unique = set(), []
    for s in stmts:
        if s["text"] not in seen:
            seen.add(s["text"])
            unique.append(s)
    stated = {s["kind"] for s in unique}
    goes_beyond = "goes_beyond" in stated
    if goes_beyond:
        stated.add("transposes_directive")
    from_text = set()
    if any(r == "transposed" for r in found.values()):
        from_text.add("transposes_directive")
    if any(r == "implemented" for r in found.values()):
        from_text.add("implements_regulation")
    kinds = stated if stated - {"goes_beyond"} else from_text
    ordered = [k for k in PRIORITY if k in kinds]
    kind = ordered[0] if ordered else "not_stated"
    wanted = {"transposes_directive": "transposed", "implements_regulation": "implemented"}
    roles = {wanted[k] for k in ordered if k in wanted}
    act_list = [act(cid, role) for cid, role in sorted(found.items()) if role in roles]
    return {"kind": kind, "kinds": ordered, "goes_beyond": goes_beyond, "statements": unique, "acts": act_list}
