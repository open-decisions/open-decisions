import hashlib
from collections.abc import Iterator
from typing import Any

import psycopg


def have(conn: psycopg.Connection, urls: list[str]) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("select url from raw.document where url = any(%s)", (urls,))
        return {r[0] for r in cur.fetchall()}


def put(conn: psycopg.Connection, url: str, content: bytes, content_type: str | None, status: int) -> str:
    digest = hashlib.sha256(content).hexdigest()
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.document (url, content, content_type, sha256, size_bytes, http_status)
            values (%s, %s, %s, %s, %s, %s)
            on conflict (url) do update set
              content = excluded.content, content_type = excluded.content_type, sha256 = excluded.sha256,
              size_bytes = excluded.size_bytes, http_status = excluded.http_status, fetched_at = now()
            """,
            (url, content, content_type, digest, len(content), status),
        )
    conn.commit()
    return digest


def unextracted(conn: psycopg.Connection) -> Iterator[tuple[str, bytes, str | None]]:
    with conn.cursor(name="unextracted") as cur:
        cur.execute(
            """
            select d.url, d.content, d.content_type from raw.document d
            left join staged.document_text t using (url)
            where t.url is null and d.http_status = 200
            """
        )
        yield from cur


def put_text(conn: psycopg.Connection, url: str, text: str, pages: int | None, extractor: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into staged.document_text (url, text, pages, extractor) values (%s, %s, %s, %s)
            on conflict (url) do update set
              text = excluded.text, pages = excluded.pages, extractor = excluded.extractor, extracted_at = now()
            """,
            (url, text, pages, extractor),
        )
    conn.commit()


def search(conn: psycopg.Connection, query: str, limit: int = 20) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            select url, pages, ts_rank(to_tsvector('german', text), q) as rank,
                   ts_headline('german', text, q, 'MaxWords=40, MinWords=20, MaxFragments=2') as snippet
            from staged.document_text, websearch_to_tsquery('german', %s) q
            where to_tsvector('german', text) @@ q
            order by rank desc limit %s
            """,
            (query, limit),
        )
        return [{"url": r[0], "pages": r[1], "rank": r[2], "snippet": r[3]} for r in cur.fetchall()]


def archive_refs(conn: psycopg.Connection, urls: list[str]) -> dict[str, str]:
    with conn.cursor() as cur:
        cur.execute("select url, sha256 from raw.document where url = any(%s) and http_status = 200", (urls,))
        return {r[0]: f"sha256:{r[1]}" for r in cur.fetchall()}
