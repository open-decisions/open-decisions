import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
DATA = ROOT / "data"
SCHEMA_PATH = ROOT / "schema" / "massnahme.schema.json"
MIGRATIONS = pathlib.Path(__file__).resolve().parents[2] / "migrations"
