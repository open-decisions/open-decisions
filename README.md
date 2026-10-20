# open-decisions

Project name of the repository and the code. The Austrian site will be published as **Durchgerechnet**; other countries get their own name.

What a political decision means for a household, in euros per year, with every number labelled and every statement sourced. No judgement, no party. Starting with Austria, built so that further EU countries can be added as new jurisdictions.

Project status: concept and data contract. No application code yet.

## Layout

| Path | Content |
| --- | --- |
| `docs/` | Project concept, methodology handbook, style guide and card format, parliament API spike (German, for Austrian funders and the editorial process); architecture (English). |
| `schema/massnahme.schema.json` | Data contract: jurisdictions, example households, bills, measures. English field names, content in the jurisdiction's language. |
| `services/core/` | Schema records, validation, Postgres migrations (raw, staged). |
| `services/ingest_at/` | Federal adapter for Austria: parliament API into raw, transform to staged, export to `data/bills/`. |
| `fixtures/` | Real API responses for tests without network. |
| `data/jurisdictions/<CC>.yaml` | Decision levels of one country: federal, states, later municipalities. |
| `data/households/<CC>.yaml` | Example households of one country. |
| `data/bills/` | Bill records, derived by the ingest pipeline: stages, documents, vote per party, identifiers. Only `measures` and `budget_office_analyses` are curated. |
| `data/measures/` | Measure records: one per provision that changes household finances. Each one is a card. |

Reference example: the abolition of the Austrian Klimabonus, `data/measures/at-2025-klimabonus.yaml`, part of bill `data/bills/AT-XXVIII-I-69.yaml`. Architecture: `docs/architecture.md`.

## Development

Python 3.13, uv workspace, one package per service under `services/`. Tooling: ruff (lint and format), pyright, pytest, pre-commit, GitHub Actions. `make setup` installs the environment and the git hooks; `make check` runs everything CI runs.

```
make setup      # uv sync, pre-commit install
make db         # start Postgres, apply migrations
make check      # ruff, pyright, pytest, record validation
make ingest     # list, details, transform, export for the current period
```

## Run

```
cp .env.example .env
make setup db
uv run open-decisions-validate
uv run ingest-at run
```

## Rules in one paragraph

A measure is included when it has been introduced in parliament as a government or governing-party bill, changes household income, taxes, transfers or mandatory expenses directly, and has a public primary source. Every number carries one of four labels: calculated, adopted, estimated, not quantifiable. Estimates carry a range and named assumptions. Government communication may only back the "what was said" element, never an effect. Nothing is published without a human release checklist. Errors are corrected publicly. Details are in `docs/Methodik-Handbuch v0.md`.

## Licence

- Code, schema and validator: GNU Affero General Public License v3.0 or later, see `LICENSE`.
- Cards, measure and bill records, household definitions and documentation: Creative Commons Attribution 4.0 International, see `LICENSE-CONTENT`.

Law texts and official documents quoted in the records are free works under Austrian copyright law. Verbatim quotes of officials rest on quotation rights and are not covered by the content licence.
