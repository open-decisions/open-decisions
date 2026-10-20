import re
from typing import Any

FORBIDDEN = re.compile(
    r"\b(entlastung\w*|belastung\w*|reform\w*|paket\w*|gerecht\w*|ungerecht\w*|fair\w*|unfair\w*|sinnvoll\w*|notwendig\w*|"
    r"großzügig\w*|hart\b|harte[nrs]?\b|sparpaket\w*|geschenk\w*|kürzung\w*|erhöhung\w*|geschont\w*|getroffen\w*)\b",
    re.IGNORECASE,
)
MAX_TITLE_WORDS = 8
MAX_SENTENCE_WORDS = 20
MAX_AVG_SENTENCE_WORDS = 15
SENTENCE_END = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ„\d])")
ABBREVIATIONS = ("Abs.", "Art.", "Nr.", "z. B.", "u. a.", "bzw.", "ca.", "Mio.", "Mrd.", "J.", "S.", "vgl.", "Z.", "lit.")

LEVEL_ONE = ("title", "law_change.summary", "unclear")
DETAIL = (
    "law_change.parameters[].name",
    "affected.who",
    "affected.condition",
    "timing.note",
    "timing.transition",
    "effects.households[].note",
    "effects.aggregate[].description",
    "effects.distribution.description",
    "assumptions[].what",
    "assumptions[].why",
    "assumptions[].alternative",
    "contradictions",
    "open_questions",
)


def _get(data: Any, path: str) -> list[tuple[str, str]]:
    def walk(node: Any, parts: list[str], where: str) -> list[tuple[str, str]]:
        if not parts:
            if isinstance(node, str):
                return [(where, node)]
            if isinstance(node, list):
                return [(f"{where}[{i}]", s) for i, s in enumerate(node) if isinstance(s, str)]
            return []
        head, rest = parts[0], parts[1:]
        if head.endswith("[]"):
            items = node.get(head[:-2], []) if isinstance(node, dict) else []
            return [hit for i, item in enumerate(items) for hit in walk(item, rest, f"{where}.{head[:-2]}[{i}]")]
        if isinstance(node, dict) and head in node:
            return walk(node[head], rest, f"{where}.{head}" if where else head)
        return []

    return walk(data, path.split("."), "")


def sentences(text: str) -> list[str]:
    protected = text
    for abbr in ABBREVIATIONS:
        protected = protected.replace(abbr, abbr.replace(".", "\u0000"))
    return [s.replace("\u0000", ".").strip() for s in SENTENCE_END.split(protected) if s.strip()]


def word_count(text: str) -> int:
    return len(re.findall(r"[\wäöüÄÖÜß€%]+", text))


def syllables(word: str) -> int:
    return max(1, len(re.findall(r"[aeiouyäöü]+", word.lower())))


def flesch_amstad(text: str) -> float | None:
    sents = sentences(text)
    words = re.findall(r"[A-Za-zÄÖÜäöüß]+", text)
    if not sents or not words:
        return None
    asl = len(words) / len(sents)
    asw = sum(syllables(w) for w in words) / len(words)
    return 180 - asl - 58.5 * asw


def check_measure_style(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for path in LEVEL_ONE + DETAIL:
        for where, text in _get(data, path):
            for m in FORBIDDEN.finditer(text):
                errors.append(f"{where}: forbidden word '{m.group(0)}'")
    for path in LEVEL_ONE:
        for where, text in _get(data, path):
            if "!" in text:
                errors.append(f"{where}: exclamation mark")
            if "?" in text:
                errors.append(f"{where}: question mark")
            for s in sentences(text):
                if word_count(s) > MAX_SENTENCE_WORDS:
                    errors.append(f"{where}: sentence has {word_count(s)} words (max {MAX_SENTENCE_WORDS}): '{s[:60]}…'")
    title = data.get("title", "")
    if word_count(title) > MAX_TITLE_WORDS:
        errors.append(f"title: {word_count(title)} words (max {MAX_TITLE_WORDS})")
    level_one_text = " ".join(t for p in ("law_change.summary", "unclear") for _, t in _get(data, p))
    sents = sentences(level_one_text)
    if sents:
        avg = sum(word_count(s) for s in sents) / len(sents)
        if avg >= MAX_AVG_SENTENCE_WORDS:
            errors.append(f"level one: average sentence length {avg:.1f} words (must be below {MAX_AVG_SENTENCE_WORDS})")
    score = flesch_amstad(level_one_text)
    if score is not None and score <= 60:
        warnings.append(f"level one: Flesch (Amstad) {score:.0f}, target above 60")
    return errors, warnings
