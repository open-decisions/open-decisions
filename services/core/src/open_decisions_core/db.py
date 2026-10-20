import os
import sys

import psycopg

from open_decisions_core import MIGRATIONS


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL is not set")
    return url


def connect() -> psycopg.Connection:
    return psycopg.connect(database_url())


def migrate(conn: psycopg.Connection) -> list[str]:
    applied = []
    with conn.cursor() as cur:
        cur.execute("create schema if not exists core")
        cur.execute("create table if not exists core.migration (name text primary key, applied_at timestamptz not null default now())")
        cur.execute("select name from core.migration")
        done = {r[0] for r in cur.fetchall()}
        for path in sorted(MIGRATIONS.glob("*.sql")):
            if path.name in done:
                continue
            cur.execute(path.read_bytes())
            cur.execute("insert into core.migration (name) values (%s)", (path.name,))
            applied.append(path.name)
    conn.commit()
    return applied


def main() -> int:
    with connect() as conn:
        applied = migrate(conn)
    print("applied:", ", ".join(applied) if applied else "nothing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
