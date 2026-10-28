import hashlib
import html
import json
import re
from typing import Any

import psycopg

SECTION_HEADING = re.compile(r"\s*<h[23][^>]*>(.*?)</h[23]>", re.S)
TAG = re.compile(r"<[^>]+>")


def release_url(url: str) -> str:
    return url.split("#")[0]


def json_url(url: str) -> str:
    return release_url(url) + "?json=TRUE"


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", fragment))).strip()


def release_parts(payload: dict[str, Any]) -> tuple[str | None, str]:
    title, body = None, ""
    for block in payload.get("content", []):
        data = block.get("data") or {}
        if title is None and data.get("title"):
            title = _text(data["title"])
        if isinstance(data.get("text"), str) and "class=pk" in data["text"]:
            body = data["text"]
    return title, body


def section_heading(body: str, anchor: str) -> str | None:
    i = body.find(f'id="{anchor}"')
    if i < 0:
        return None
    rest = body[body.find(">", i) + 1 :]
    rest = rest.removeprefix("</a>")
    m = SECTION_HEADING.match(rest)
    return _text(m.group(1)) if m else None


def have(conn: psycopg.Connection, urls: list[str]) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("select url from raw.document where url = any(%s) and http_status = 200", (urls,))
        return {r[0] for r in cur.fetchall()}


def store_release(conn: psycopg.Connection, url: str, content: bytes, status: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.document (url, content, content_type, sha256, size_bytes, http_status)
            values (%s, %s, 'application/json', %s, %s, %s)
            on conflict (url) do update set content = excluded.content, sha256 = excluded.sha256,
              size_bytes = excluded.size_bytes, http_status = excluded.http_status, fetched_at = now()
            """,
            (url, content, hashlib.sha256(content).hexdigest(), len(content), status),
        )
    conn.commit()


def load_release(conn: psycopg.Connection, url: str) -> dict[str, Any] | None:
    with conn.cursor() as cur:
        cur.execute("select content from raw.document where url = %s and http_status = 200", (url,))
        row = cur.fetchone()
    return json.loads(bytes(row[0])) if row else None


def upsert_section(conn: psycopg.Connection, url: str, title: str | None, heading: str | None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into staged.press_section (url, release_url, release_title, heading) values (%s, %s, %s, %s)
            on conflict (url) do update set release_title = excluded.release_title, heading = excluded.heading, extracted_at = now()
            """,
            (url, release_url(url), title, heading),
        )
    conn.commit()


def sections(conn: psycopg.Connection) -> dict[str, dict[str, str | None]]:
    with conn.cursor() as cur:
        cur.execute("select url, release_title, heading from staged.press_section")
        return {r[0]: {"release_title": r[1], "heading": r[2]} for r in cur.fetchall()}
