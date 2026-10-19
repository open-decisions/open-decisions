# Politische Entscheidungen verständlich bewertet

What a political decision means for a household, in euros per year, with every number labelled and every statement sourced. No judgement, no party. Starting with Austria, built so that further EU countries can be added as new jurisdictions.

Project status: concept and data contract. No application code yet.

## Layout

| Path | Content |
| --- | --- |
| `docs/` | Project concept, methodology handbook, style guide and card format, parliament API spike. German, written for Austrian funders and the editorial process. |
| `schema/massnahme.schema.json` | Data contract: bill, measure, example households. English field names, content in the jurisdiction's language. |
| `schema/validate.py` | Validates all records against the schema and checks cross-references. |
| `households/<CC>.yaml` | Example households of one jurisdiction. |
| `vorhaben/` | Bill records: parliamentary stages, documents, vote per party. |
| `massnahmen/` | Measure records: one per provision that changes household finances. Each one is a card. |

Reference example: the abolition of the Austrian Klimabonus, `massnahmen/at-2025-klimabonus.yaml`, part of bill `vorhaben/AT-XXVIII-I-69.yaml`.

## Validate

```
uv run --with pyyaml --with jsonschema schema/validate.py
```

## Rules in one paragraph

A measure is included when it has been introduced in parliament as a government or governing-party bill, changes household income, taxes, transfers or mandatory expenses directly, and has a public primary source. Every number carries one of four labels: calculated, adopted, estimated, not quantifiable. Estimates carry a range and named assumptions. Government communication may only back the "what was said" element, never an effect. Nothing is published without a human release checklist. Errors are corrected publicly. Details are in `docs/Methodik-Handbuch v0.md`.

## Licence

- Code, schema and validator: GNU Affero General Public License v3.0 or later, see `LICENSE`.
- Cards, measure and bill records, household definitions and documentation: Creative Commons Attribution 4.0 International, see `LICENSE-CONTENT`.

Law texts and official documents quoted in the records are free works under Austrian copyright law. Verbatim quotes of officials rest on quotation rights and are not covered by the content licence.
