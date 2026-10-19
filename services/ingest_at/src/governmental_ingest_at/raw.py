import hashlib
import json
from typing import Any

import psycopg

from governmental_ingest_at import JURISDICTION
from governmental_ingest_at.client import list_rows, parse_his_url


def _hash(payload: Any) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def upsert_list(conn: psycopg.Connection, listing: dict[str, Any]) -> tuple[int, int]:
    inserted = changed = 0
    with conn.cursor() as cur:
        for row in list_rows(listing):
            key = parse_his_url(row.get("HIS_URL") or "")
            if key is None:
                continue
            gp, ityp, inr = key
            h = _hash(row)
            cur.execute(
                """
                insert into raw.parliament_list_item (jurisdiction, gp, ityp, inr, payload, hash)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (jurisdiction, gp, ityp, inr) do update set
                  last_seen = now(),
                  payload = excluded.payload,
                  changed_at = case when raw.parliament_list_item.hash <> excluded.hash
                               then now() else raw.parliament_list_item.changed_at end,
                  hash = excluded.hash
                returning (xmax = 0) as inserted, (changed_at = now()) as changed
                """,
                (JURISDICTION, gp, ityp, inr, psycopg.types.json.Jsonb(row), h),
            )
            ins, chg = cur.fetchone()
            inserted += int(ins)
            changed += int(chg and not ins)
    conn.commit()
    return inserted, changed


def upsert_item(conn: psycopg.Connection, gp: str, ityp: str, inr: str, payload: dict[str, Any]) -> bool:
    h = _hash(payload)
    with conn.cursor() as cur:
        cur.execute(
            """
            insert into raw.parliament_item (jurisdiction, gp, ityp, inr, payload, hash)
            values (%s, %s, %s, %s, %s, %s)
            on conflict (jurisdiction, gp, ityp, inr) do update set
              fetched_at = now(),
              payload = excluded.payload,
              changed_at = case when raw.parliament_item.hash <> excluded.hash then now() else raw.parliament_item.changed_at end,
              hash = excluded.hash
            returning (changed_at = now()) as changed
            """,
            (JURISDICTION, gp, ityp, inr, psycopg.types.json.Jsonb(payload), h),
        )
        changed = cur.fetchone()[0]
    conn.commit()
    return changed


def pending_items(
    conn: psycopg.Connection, gp: str, ityps: tuple[str, ...], arts: tuple[str, ...], refetch_all: bool = False
) -> list[tuple[str, str, str]]:
    sql = """
        select l.gp, l.ityp, l.inr
        from raw.parliament_list_item l
        left join raw.parliament_item i using (jurisdiction, gp, ityp, inr)
        where l.jurisdiction = %s and l.gp = %s and l.ityp = any(%s)
          and l.payload->>'Art' = any(%s)
          and (%s or i.inr is null or l.changed_at > i.fetched_at)
        order by l.ityp, (l.inr)::integer
    """
    with conn.cursor() as cur:
        cur.execute(sql, (JURISDICTION, gp, list(ityps), list(arts), refetch_all))
        return [tuple(r) for r in cur.fetchall()]


def items(conn: psycopg.Connection, gp: str, ityps: tuple[str, ...], doktyps: tuple[str, ...]):
    with conn.cursor() as cur:
        cur.execute(
            """
            select gp, ityp, inr, payload, fetched_at from raw.parliament_item
            where jurisdiction = %s and gp = %s and ityp = any(%s) and payload->'content'->>'doktyp' = any(%s)
            """,
            (JURISDICTION, gp, list(ityps), list(doktyps)),
        )
        yield from cur.fetchall()
