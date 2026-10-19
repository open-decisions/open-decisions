import json
import pathlib
import sys

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA = json.loads((ROOT / "schema" / "massnahme.schema.json").read_text(encoding="utf-8"))
KINDS = {"bill": "#/$defs/bill", "measure": "#/$defs/measure", "households": "#/$defs/households"}
ROLE_FOR_SAID = "government_communication"


def validator_for(kind: str) -> jsonschema.Draft202012Validator:
    sub = {"$schema": SCHEMA["$schema"], "$ref": KINDS[kind], "$defs": SCHEMA["$defs"]}
    return jsonschema.Draft202012Validator(sub)


def load(path: pathlib.Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def household_ids(jurisdiction: str) -> set[str] | None:
    path = ROOT / "households" / f"{jurisdiction}.yaml"
    if not path.exists():
        return None
    return {h["id"] for h in load(path).get("households", [])}


def walk_refs(node):
    if isinstance(node, dict):
        if "source" in node and "ref" in node:
            yield "source", node["source"]
        if isinstance(node.get("assumptions"), list):
            for a in node["assumptions"]:
                if isinstance(a, str):
                    yield "assumption", a
        for v in node.values():
            yield from walk_refs(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk_refs(v)


def check_measure(data) -> list[str]:
    errors = []
    sources = {s["id"]: s for s in data.get("sources", [])}
    assumptions = {a["id"] for a in data.get("assumptions", [])}
    for kind, ref in walk_refs(data):
        if kind == "source" and ref not in sources:
            errors.append(f"unknown source id: {ref}")
        if kind == "assumption" and ref not in assumptions:
            errors.append(f"unknown assumption id: {ref}")
    for s in data.get("said", {}).get("sources", []):
        src = sources.get(s.get("source"))
        if src and src["role"] != ROLE_FOR_SAID:
            errors.append(f"said must cite {ROLE_FOR_SAID}, {s['source']} is {src['role']}")
    for kind, ref in walk_refs({k: v for k, v in data.items() if k != "said"}):
        if kind == "source" and ref in sources and sources[ref]["role"] == ROLE_FOR_SAID:
            errors.append(f"{ROLE_FOR_SAID} source {ref} may only back the said element")
    if not data.get("bill", "").startswith(data.get("jurisdiction", "") + "/"):
        errors.append("bill id must start with the measure's jurisdiction")
    if not data.get("id", "").startswith(data.get("jurisdiction", "").lower() + "-"):
        errors.append("measure id must start with the lower-case jurisdiction")
    known = household_ids(data.get("jurisdiction", ""))
    used = [h["household"] for h in data.get("effects", {}).get("households", [])]
    if known is None:
        errors.append(f"no households file for jurisdiction {data.get('jurisdiction')}")
    else:
        for h in used:
            if h not in known:
                errors.append(f"unknown household id: {h}")
        for h in sorted(known - set(used)):
            errors.append(f"household {h} has no entry in effects.households")
    return errors


def check_bill(data) -> list[str]:
    errors = []
    if not data.get("id", "").startswith(data.get("jurisdiction", "") + "/"):
        errors.append("bill id must start with the jurisdiction")
    for m in data.get("measures", []):
        if not (ROOT / "massnahmen" / f"{m}.yaml").exists():
            errors.append(f"measure file missing: massnahmen/{m}.yaml")
    return errors


def check(path: pathlib.Path) -> list[str]:
    data = load(path)
    kind = data.get("kind") if isinstance(data, dict) else None
    if kind not in KINDS:
        return [f"kind must be one of {sorted(KINDS)}, got {kind!r}"]
    errors = [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}" for e in validator_for(kind).iter_errors(data)]
    if errors:
        return errors
    if kind == "measure":
        errors += check_measure(data)
        if path.stem != data["id"]:
            errors.append(f"file name must equal id ({data['id']})")
    if kind == "bill":
        errors += check_bill(data)
    if kind == "households" and path.stem != data["jurisdiction"]:
        errors.append(f"file name must equal jurisdiction ({data['jurisdiction']})")
    return errors


def main() -> int:
    files = [pathlib.Path(a) for a in sys.argv[1:]] or (
        sorted((ROOT / "households").glob("*.yaml")) + sorted((ROOT / "vorhaben").glob("*.yaml")) + sorted((ROOT / "massnahmen").glob("*.yaml"))
    )
    failed = False
    for f in files:
        errs = check(f)
        shown = f.relative_to(ROOT) if f.resolve().is_relative_to(ROOT) else f
        print(f"{'FAIL' if errs else 'ok  '} {shown}")
        for e in errs:
            print(f"      {e}")
        failed |= bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
