# AGENTS.md

Guidance for coding assistants and new contributors. CLAUDE.md imports this file; other tools read it directly.

## What this is

Curated records of political decisions and what they mean for households, starting with Austria. The product is the record: a decision, its effect per example household with a confidence label, the official message next to the law text, and who voted for it. Neutrality is the core constraint: no judgement words, no scores for parties, every number labelled, every statement sourced. Read `docs/architecture.md` first, then `docs/Methodik-Handbuch v0.md` for the editorial rules.

## Layout

- `schema/massnahme.schema.json` is the data contract. It is the source of truth; models are derived from it, never written by hand.
- `data/` holds the records. `jurisdictions`, `households` and `measures` are curated and reviewed in pull requests. `bills` are derived: the ingest pipeline generates them, and only the fields `measures` and `budget_office_analyses` on a bill are edited by hand.
- `services/core` has schema loading, validation and Postgres migrations (`raw`, `staged`). `services/ingest_at` is the federal adapter for Austria. One package per service; a service becomes a running process only when it has a different runtime, cost profile or data sensitivity.
- `fixtures/` holds real API responses so tests run without network.
- `docs/` holds the concept (German), the methodology and style guide (German), the architecture (English), the API spike notes and the decision log.

## Commands

```
make setup      # uv sync and pre-commit install
make db         # docker compose Postgres on port 5433 and migrations; needs .env from .env.example
make check      # ruff, pyright, pytest, record validation; same as CI
make ingest     # list, details, transform, export for the current legislative period
```

Run `make check` before opening a pull request. Pre-commit runs the same checks on commit.

## Conventions

- Code, schema, commit messages and this file are English. Record content is in the language of its jurisdiction (`lang`), German for Austria. Concept and methodology docs stay German because their readers are Austrian.
- Python 3.13, uv workspace, ruff with the rule set in `pyproject.toml`, pyright standard mode, pytest with importlib mode. No comments or docstrings unless the reason cannot be seen in the code: a library quirk, a non-obvious external constraint, or why an obvious alternative was rejected.
- Every number in a record carries one label: `calculated`, `adopted`, `estimated` (with range and assumptions) or `not_quantifiable` (with reason). Government communication may only back the "said" element.
- Identifiers link outward: ELI for acts, EuroVoc for topics, Wikidata for parties, ISO 3166 for jurisdictions. Do not invent identifiers.
- Decisions with lasting effect go into `docs/decisions.md` with alternatives and reason. Methodology changes need a decision log entry.
- Pipeline stages write only their own layer: adapters write `raw`, the transform writes `staged`, the export writes `data/bills`. Nothing writes curated records except humans through pull requests.
- Do not add dependencies for one-off needs. Prefer the standard library and the few libraries already in use.
- Licences: code AGPL-3.0-or-later, content and data CC BY 4.0. Quoted law texts are free works; quotes of officials rest on quotation rights.

## Things that look like bugs but are not

- `data/bills` contains opposition bills that never passed. The tracker needs completeness; the governing-party rule applies to measure selection only.
- The Klimabonus example labels plain arithmetic as `estimated`, not `calculated`, because the methodology reserves `calculated` for the microsimulation. See the decision log.
- The parliament's item type `I` covers all numbered Beilagen; bills are filtered by document type `RV` and `A`.
