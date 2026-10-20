import argparse
import sys
import time

import httpx

from open_decisions_core.db import connect
from open_decisions_documents import extract, store, urls

USER_AGENT = "open-decisions-documents/0.1 (open data archive; CC BY 4.0 consumer)"


def cmd_fetch(args) -> int:
    wanted = urls.record_urls()
    with connect() as conn:
        present = have_all(conn, list(wanted))
        pending = [u for u in wanted if u not in present or args.all]
        print(f"{len(wanted)} urls referenced, {len(pending)} to fetch")
        client = httpx.Client(timeout=120, headers={"User-Agent": USER_AGENT}, follow_redirects=True)
        try:
            for n, url in enumerate(pending, 1):
                try:
                    r = client.get(url)
                    store.put(conn, url, r.content, r.headers.get("content-type"), r.status_code)
                    if r.status_code != 200:
                        print(f"  {n}/{len(pending)} {r.status_code} {url}")
                except httpx.HTTPError as e:
                    print(f"  {n}/{len(pending)} error {url}: {e}")
                if n % 50 == 0:
                    print(f"  {n}/{len(pending)}")
                time.sleep(args.delay)
        finally:
            client.close()
    return 0


def have_all(conn, all_urls: list[str]) -> set[str]:
    present: set[str] = set()
    for i in range(0, len(all_urls), 500):
        present |= store.have(conn, all_urls[i : i + 500])
    return present


def cmd_extract(args) -> int:
    done = failed = 0
    with connect() as conn, connect() as writer:
        for url, content, content_type in store.unextracted(conn):
            try:
                text, pages, extractor = extract.extract(bytes(content), content_type, url)
            except Exception as e:
                failed += 1
                print(f"  failed {url}: {e}")
                continue
            store.put_text(writer, url, text, pages, extractor)
            done += 1
            if done % 50 == 0:
                print(f"  {done} extracted")
    print(f"extracted {done}, failed {failed}")
    return 1 if failed and not done else 0


def cmd_search(args) -> int:
    with connect() as conn:
        hits = store.search(conn, " ".join(args.terms), args.limit)
    for h in hits:
        print(f"{h['url']}  (pages: {h['pages']}, rank {h['rank']:.3f})")
        print("   " + h["snippet"].replace("\n", " ")[:400])
    return 0


def cmd_archive_refs(args) -> int:
    wanted = urls.record_urls(("measure",))
    with connect() as conn:
        refs = store.archive_refs(conn, list(wanted))
    missing = [u for u in wanted if u not in refs]
    for u, ref in refs.items():
        print(f"{ref}  {u}  ({', '.join(wanted[u])})")
    for u in missing:
        print(f"MISSING  {u}  ({', '.join(wanted[u])})")
    return 1 if missing else 0


def main() -> int:
    p = argparse.ArgumentParser(prog="documents")
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--all", action="store_true")
    f.add_argument("--delay", type=float, default=0.5)
    f.set_defaults(fn=cmd_fetch)
    sub.add_parser("extract").set_defaults(fn=cmd_extract)
    s = sub.add_parser("search")
    s.add_argument("terms", nargs="+")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(fn=cmd_search)
    sub.add_parser("archive-refs").set_defaults(fn=cmd_archive_refs)
    r = sub.add_parser("run")
    r.set_defaults(fn=lambda a: cmd_fetch(argparse.Namespace(all=False, delay=0.5)) or cmd_extract(a))
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
