import argparse
import sys

from open_decisions_core import DATA
from open_decisions_core.db import connect
from open_decisions_core.records import check, dump, load
from open_decisions_ingest_at import BILL_TYPES, JURISDICTION
from open_decisions_ingest_at import press as press_layer
from open_decisions_ingest_at import raw as raw_layer
from open_decisions_ingest_at import staged as staged_layer
from open_decisions_ingest_at.client import ParliamentClient
from open_decisions_ingest_at.eu import relation
from open_decisions_ingest_at.transform import bill_from_item, record_from_bill

BILL_ITYPS = ("I", "A")
BILL_DOKTYPS = tuple(BILL_TYPES)


def cmd_list(args) -> int:
    client = ParliamentClient()
    try:
        listing = client.list_items(args.gp)
    finally:
        client.close()
    with connect() as conn:
        inserted, changed = raw_layer.upsert_list(conn, listing)
    print(f"list {args.gp}: {listing.get('count')} items, {inserted} new, {changed} changed")
    return 0


def cmd_details(args) -> int:
    with connect() as conn:
        pending = raw_layer.pending_items(conn, args.gp, BILL_ITYPS, BILL_DOKTYPS, refetch_all=args.all)
        if args.limit:
            pending = pending[: args.limit]
        print(f"fetching {len(pending)} items")
        client = ParliamentClient()
        try:
            for n, (gp, ityp, inr) in enumerate(pending, 1):
                payload = client.get_item(gp, ityp, inr)
                changed = raw_layer.upsert_item(conn, gp, ityp, inr, payload)
                if n % 25 == 0 or changed:
                    print(f"  {n}/{len(pending)} {gp}/{ityp}/{inr}{' changed' if changed else ''}")
        finally:
            client.close()
    return 0


def cmd_transform(args) -> int:
    count = 0
    with connect() as conn:
        for gp, ityp, inr, payload, fetched_at in list(raw_layer.items(conn, args.gp, BILL_ITYPS, BILL_DOKTYPS)):
            try:
                bill = bill_from_item(payload, fetched_at)
            except Exception as e:
                print(f"  skip {gp}/{ityp}/{inr}: {e}")
                continue
            staged_layer.upsert_bill(conn, bill)
            count += 1
    print(f"transformed {count} bills")
    return 0


def cmd_eu(args) -> int:
    counts: dict[str, int] = {}
    with connect() as conn:
        bills = staged_layer.bills(conn, JURISDICTION, args.gp, BILL_ITYPS)
        for bill in bills:
            rel = relation(staged_layer.bill_documents(conn, bill["id"]))
            staged_layer.upsert_eu(conn, bill["id"], rel)
            counts[rel["kind"]] = counts.get(rel["kind"], 0) + 1
    print("eu relation:", ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    return 0


def cmd_press(args) -> int:
    with connect() as conn:
        bills = staged_layer.bills(conn, JURISDICTION, args.gp, BILL_ITYPS)
        items = [p["url"] for b in bills for p in b.get("press", [])]
        releases = sorted({press_layer.json_url(u) for u in items})
        missing = [u for u in releases if u not in press_layer.have(conn, releases)]
        print(f"{len(releases)} press releases referenced, {len(missing)} to fetch")
        client = ParliamentClient()
        try:
            for n, url in enumerate(missing, 1):
                content, _ = client.get_document(url.replace(client.base_url, ""))
                press_layer.store_release(conn, url, content, 200)
                if n % 50 == 0:
                    print(f"  {n}/{len(missing)}")
        finally:
            client.close()
        headed = 0
        for url in items:
            payload = press_layer.load_release(conn, press_layer.json_url(url))
            if payload is None:
                continue
            title, body = press_layer.release_parts(payload)
            heading = press_layer.section_heading(body, url.split("#")[1]) if "#" in url else None
            press_layer.upsert_section(conn, url, title, heading)
            headed += heading is not None
    print(f"press sections: {len(items)}, with own heading {headed}")
    return 0


def cmd_export(args) -> int:
    out_dir = DATA / "bills"
    written = failed = 0
    with connect() as conn:
        rows = staged_layer.bills(conn, JURISDICTION, args.gp, BILL_ITYPS)
        eu = staged_layer.eu_relations(conn)
        sections = press_layer.sections(conn)
    for bill in rows:
        if bill["id"] in eu:
            bill["eu_relation"] = eu[bill["id"]]
        for p in bill.get("press", []):
            if heading := (sections.get(p["url"]) or {}).get("heading"):
                p["heading"] = heading
    expected = {out_dir / (b["id"].replace("/", "-") + ".yaml") for b in rows}
    for stale in sorted(set(out_dir.glob(f"{JURISDICTION}-{args.gp}-*.yaml")) - expected):
        stale.unlink()
        print(f"  removed stale {stale.name}")
    for bill in rows:
        if args.decided_only and bill["stage"] in ("introduced", "committee"):
            continue
        path = out_dir / (bill["id"].replace("/", "-") + ".yaml")
        curated = load(path) if path.exists() else None
        record = record_from_bill(bill, curated)
        errors = check(record, path)
        if errors:
            failed += 1
            print(f"  invalid {bill['id']}: {errors[0]}")
            continue
        dump(record, path)
        written += 1
    print(f"exported {written} bills to {out_dir}, {failed} invalid")
    return 1 if failed else 0


def main() -> int:
    p = argparse.ArgumentParser(prog="ingest-at")
    p.add_argument("--gp", default="XXVIII")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    d = sub.add_parser("details")
    d.add_argument("--all", action="store_true")
    d.add_argument("--limit", type=int, default=0)
    d.set_defaults(fn=cmd_details)
    sub.add_parser("transform").set_defaults(fn=cmd_transform)
    sub.add_parser("eu").set_defaults(fn=cmd_eu)
    sub.add_parser("press").set_defaults(fn=cmd_press)
    e = sub.add_parser("export")
    e.add_argument("--decided-only", action="store_true")
    e.set_defaults(fn=cmd_export)
    r = sub.add_parser("run")
    r.add_argument("--decided-only", action="store_true")
    r.set_defaults(
        fn=lambda a: (
            cmd_list(a)
            or cmd_details(argparse.Namespace(gp=a.gp, all=False, limit=0))
            or cmd_transform(a)
            or cmd_eu(a)
            or cmd_press(a)
            or cmd_export(a)
        )
    )
    args = p.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
