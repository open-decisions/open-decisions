from typing import Any

import psycopg
from psycopg.types.json import Jsonb


def upsert_bill(conn: psycopg.Connection, bill: dict[str, Any]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into staged.bill (id, jurisdiction, gp, ityp, inr, type, title, citation, parliament_url, introduced, introduced_by,
              stage, source_status, gazette, gazette_url, eli, eurovoc, topics, keywords, documents, pre_parliamentary, vote,
              source_updated, fetched_at, transformed_at)
            values (%(id)s, %(jurisdiction)s, %(gp)s, %(ityp)s, %(inr)s, %(type)s, %(title)s, %(citation)s, %(parliament_url)s,
              %(introduced)s, %(introduced_by)s, %(stage)s, %(source_status)s, %(gazette)s, %(gazette_url)s, %(eli)s, %(eurovoc)s,
              %(topics)s, %(keywords)s, %(documents)s, %(pre_parliamentary)s, %(vote)s, %(source_updated)s, %(fetched_at)s, now())
            on conflict (id) do update set
              type = excluded.type, title = excluded.title, citation = excluded.citation, parliament_url = excluded.parliament_url,
              introduced = excluded.introduced, introduced_by = excluded.introduced_by, stage = excluded.stage,
              source_status = excluded.source_status, gazette = excluded.gazette, gazette_url = excluded.gazette_url, eli = excluded.eli,
              eurovoc = excluded.eurovoc, topics = excluded.topics, keywords = excluded.keywords, documents = excluded.documents,
              pre_parliamentary = excluded.pre_parliamentary, vote = excluded.vote, source_updated = excluded.source_updated,
              fetched_at = excluded.fetched_at, transformed_at = now()
            """,
            {
                **{
                    k: bill[k]
                    for k in (
                        "id",
                        "jurisdiction",
                        "gp",
                        "ityp",
                        "inr",
                        "type",
                        "title",
                        "citation",
                        "parliament_url",
                        "introduced",
                        "stage",
                        "source_status",
                        "gazette",
                        "gazette_url",
                        "eli",
                        "source_updated",
                        "fetched_at",
                    )
                },
                "introduced_by": Jsonb(bill["introduced_by"]),
                "eurovoc": Jsonb(bill["eurovoc"]),
                "topics": Jsonb(bill["topics"]),
                "keywords": Jsonb(bill["keywords"]),
                "documents": Jsonb(bill["documents"]),
                "pre_parliamentary": Jsonb(bill["pre_parliamentary"]),
                "vote": Jsonb({**bill["vote"], "date": bill["vote"]["date"].isoformat()}) if bill["vote"] else None,
            },
        )
        cur.execute("delete from staged.bill_phase where bill_id = %s", (bill["id"],))
        cur.executemany(
            "insert into staged.bill_phase (bill_id, seq, phase, chamber, date, text, url) values (%s, %s, %s, %s, %s, %s, %s)",
            [(bill["id"], i, p["phase"], p["chamber"], p["date"], p["text"], p["url"]) for i, p in enumerate(bill["phases"])],
        )
    conn.commit()


def bills(conn: psycopg.Connection, jurisdiction: str, gp: str, ityps: tuple[str, ...]):
    with conn.cursor() as cur:
        cur.execute(
            "select * from staged.bill where jurisdiction = %s and gp = %s and ityp = any(%s) order by ityp, inr::integer",
            (jurisdiction, gp, list(ityps)),
        )
        cols = [d.name for d in cur.description]
        rows = [dict(zip(cols, r, strict=False)) for r in cur.fetchall()]
    with conn.cursor() as cur:
        for b in rows:
            cur.execute(
                "select phase, chamber, date, text, url from staged.bill_phase where bill_id = %s order by seq",
                (b["id"],),
            )
            b["phases"] = [dict(zip(("phase", "chamber", "date", "text", "url"), r, strict=False)) for r in cur.fetchall()]
            if b["vote"]:
                from datetime import date

                b["vote"]["date"] = date.fromisoformat(b["vote"]["date"])
    return rows
