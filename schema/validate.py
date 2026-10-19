import json
import pathlib
import sys

import jsonschema
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SCHEMA = json.loads((ROOT / "schema" / "massnahme.schema.json").read_text(encoding="utf-8"))
KINDS = {
    "jurisdictions": "#/$defs/jurisdictions",
    "households": "#/$defs/households",
    "bill": "#/$defs/bill",
    "measure": "#/$defs/measure",
}
ROLE_FOR_SAID = "government_communication"


def validator_for(kind: str) -> jsonschema.Draft202012Validator:
    sub = {"$schema": SCHEMA["$schema"], "$ref": KINDS[kind], "$defs": SCHEMA["$defs"]}
    return jsonschema.Draft202012Validator(sub)


def load(path: pathlib.Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def country_of(jurisdiction: str) -> str:
    return jurisdiction.split("-")[0]


def registered_jurisdictions(country: str) -> set[str] | None:
    path = DATA / "jurisdictions" / f"{country}.yaml"
    if not path.exists():
        return None
    return {e["code"] for e in load(path).get("entries", [])}


def household_ids(country: str) -> set[str] | None:
    path = DATA / "households" / f"{country}.yaml"
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


def check_jurisdiction(data) -> list[str]:
    j = data.get("jurisdiction", "")
    known = registered_jurisdictions(country_of(j))
    if known is None:
        return [f"no jurisdictions file for country {country_of(j)}"]
    if j not in known:
        return [f"jurisdiction {j} is not registered in data/jurisdictions/{country_of(j)}.yaml"]
    return []


def check_measure(data) -> list[str]:
    errors = check_jurisdiction(data)
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
    j = data.get("jurisdiction", "")
    if not data.get("bill", "").startswith(j + "/"):
        errors.append("bill id must start with the measure's jurisdiction")
    if not data.get("id", "").startswith(j.lower() + "-"):
        errors.append("measure id must start with the lower-case jurisdiction")
    known = household_ids(country_of(j))
    used = [h["household"] for h in data.get("effects", {}).get("households", [])]
    if known is None:
        errors.append(f"no households file for country {country_of(j)}")
    else:
        for h in used:
            if h not in known:
                errors.append(f"unknown household id: {h}")
        for h in sorted(known - set(used)):
            errors.append(f"household {h} has no entry in effects.households")
    return errors


def check_bill(data) -> list[str]:
    errors = check_jurisdiction(data)
    if not data.get("id", "").startswith(data.get("jurisdiction", "") + "/"):
        errors.append("bill id must start with the jurisdiction")
    for m in data.get("measures", []):
        if not (DATA / "measures" / f"{m}.yaml").exists():
            errors.append(f"measure file missing: data/measures/{m}.yaml")
    return errors


def check_jurisdictions(data) -> list[str]:
    errors = []
    codes = [e["code"] for e in data.get("entries", [])]
    for c in codes:
        if country_of(c) != data.get("country"):
            errors.append(f"entry {c} does not belong to country {data.get('country')}")
    if len(codes) != len(set(codes)):
        errors.append("duplicate jurisdiction codes")
    if data.get("country") not in codes:
        errors.append("the national level itself must be an entry")
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
    elif kind == "bill":
        errors += check_bill(data)
    elif kind == "households":
        if path.stem != data["jurisdiction"]:
            errors.append(f"file name must equal jurisdiction ({data['jurisdiction']})")
    elif kind == "jurisdictions":
        errors += check_jurisdictions(data)
        if path.stem != data["country"]:
            errors.append(f"file name must equal country ({data['country']})")
    return errors


def main() -> int:
    files = [pathlib.Path(a) for a in sys.argv[1:]] or [
        f for sub in ("jurisdictions", "households", "bills", "measures") for f in sorted((DATA / sub).glob("*.yaml"))
    ]
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
