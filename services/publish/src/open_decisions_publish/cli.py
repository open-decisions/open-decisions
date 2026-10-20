import argparse
import json
import pathlib
import sys

from jinja2 import Environment, PackageLoader, select_autoescape

from open_decisions_core import DATA, ROOT
from open_decisions_core.records import load
from open_decisions_publish.cards import card_view


def render(out: pathlib.Path) -> list[pathlib.Path]:
    env = Environment(loader=PackageLoader("open_decisions_publish", "templates"), autoescape=select_autoescape(["html"]))
    card_tpl, index_tpl = env.get_template("card.html.j2"), env.get_template("index.html.j2")
    (out / "cards").mkdir(parents=True, exist_ok=True)
    written, cards = [], []
    for path in sorted((DATA / "measures").glob("*.yaml")):
        card = card_view(load(path))
        cards.append(card)
        html_path = out / "cards" / f"{card['id']}.html"
        html_path.write_text(card_tpl.render(card=card), encoding="utf-8")
        json_path = out / "cards" / f"{card['id']}.json"
        json_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        written += [html_path, json_path]
    index = out / "index.html"
    index.write_text(index_tpl.render(cards=cards), encoding="utf-8")
    return [*written, index]


def main() -> int:
    p = argparse.ArgumentParser(prog="publish")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("--out", default=str(ROOT / "build"))
    args = p.parse_args()
    files = render(pathlib.Path(args.out))
    print(f"rendered {len(files)} files to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
