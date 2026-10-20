import html
import re
import shutil
import subprocess
import tempfile

TAG = re.compile(r"<[^>]+>")
DROP = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
BLOCK = re.compile(r"</?(p|div|br|tr|li|h[1-6]|table|section)\b[^>]*>", re.I)
FORM_FEED = "\f"


def html_to_text(raw: bytes | str) -> str:
    s = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
    s = DROP.sub(" ", s)
    s = BLOCK.sub("\n", s)
    s = TAG.sub(" ", s)
    s = html.unescape(s)
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in s.splitlines()]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def pdftotext_available() -> bool:
    return shutil.which("pdftotext") is not None


def pdf_to_text(content: bytes) -> tuple[str, int]:
    if not pdftotext_available():
        raise RuntimeError("pdftotext (poppler) is not installed")
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(content)
        f.flush()
        out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, check=True)
    text = out.stdout.decode("utf-8", errors="replace")
    pages = text.count(FORM_FEED) + (1 if text and not text.endswith(FORM_FEED) else 0)
    return text, pages


def extract(content: bytes, content_type: str | None, url: str) -> tuple[str, int | None, str]:
    ct = (content_type or "").lower()
    if "pdf" in ct or url.lower().endswith(".pdf") or content[:5] == b"%PDF-":
        text, pages = pdf_to_text(content)
        return text, pages, "pdftotext"
    return html_to_text(content), None, "html"
