# Architecture

Status: target architecture, October 2026. Nothing below is built yet except the schema, the records and the validator. German concept documents live next to this file; this document is in English because it describes code.

## Principles

1. **The curated record is the product.** A decision, its measured effect per household type, the official message next to the law, and who voted for it, in one schema, with a label on every number and a source on every statement. Raw open data already exists elsewhere; the curated, linked, reviewed record does not.
2. **Boundaries without network calls where possible.** Components are separate packages with explicit contracts and their own tests, which is what humans and AI agents work well on. A component becomes a running service only when it has a different runtime, a different cost profile, or different data sensitivity.
3. **Git is the curated content database, Postgres is the system of record for ingested data.** Measures, households, jurisdictions and assumptions are YAML files reviewed in pull requests; versioning, public corrections and the changelog per card come for free. Everything machine-produced (API payloads, documents, extracted text, phases, votes, later feedback and embeddings) lives in Postgres from day one. Bill records are derived: the ingest pipeline generates them from Postgres and the YAML in git is an export that keeps the site buildable offline and auditable; only the fields `measures` and `budget_office_analyses` on a bill are curated and preserved across exports.
4. **One schema, several surfaces.** Files, bulk exports, a REST API and an MCP server all serve the same records. The label and the sources travel with every number on every surface.
5. **Link, don't invent.** Laws carry their ELI, topics their EuroVoc descriptors, parties and people their Wikidata ids. Jurisdictions use ISO 3166 codes. This is what makes records comparable across levels and later across countries.
6. **Content in the language of the jurisdiction, code in English.** Sources and readers are local. The contract is not.
7. **Audiences are views, not texts.** Level one for readers without prior knowledge, level two for the politically literate and for experts, raw records and API for research and media. All three render the same record; nothing is written separately per audience. A generated intermediate text, if ever wanted, is checked against the record by the eval set.
8. **Editions are configuration, not forks.** One site codebase serves every country and brand. An edition names jurisdiction, language, chambers and stage names, theme tokens and feature flags. Rendering rules stay in the publish step so a correction applies to every edition at once.
9. **Everything is open source.** Code including the site and every edition under AGPL-3.0-or-later, content and data under CC BY 4.0. Explanations for citizens are never behind a paywall; revenue, if any, comes from memberships, media partnerships, grants, professional API quotas or editions for partner organisations.

## Layers

| Layer | Store | Content | Exists |
| --- | --- | --- | --- |
| Records | git, `data/` | jurisdictions, households, measures (curated); bills (derived export); later party positions | yes |
| Results | git, `data/results/` | simulation outputs, cached and versioned | planned, Phase 1 |
| Warehouse | Postgres | raw: API payloads and fetched documents, append-only; staged: normalized bills, phases, votes, documents, text; curated: the git records loaded for queries; later feedback, embeddings, chat cache | raw and staged in Phase 0 |
| Exports | release artifacts | the public dataset as Parquet and JSON, versioned, later with a DOI | planned, Phase 3 |
| API | FastAPI | read access to records and results, write access for feedback | planned, Phase 4 |
| MCP | MCP server on the same models | tools for assistants: search measures, get measure, get bill, household effect, list sources | planned, Phase 4 |
| Site | Astro, static output | cards, detail pages, methodology, corrections, tracker; interactive islands | planned, Phase 1 |

Warehouse layers: `raw` holds API responses and fetched documents as JSONB and bytes with URL, fetch time and hash, append-only and never edited. `staged` holds normalized tables rebuilt from raw at any time. `curated` holds the git records loaded for queries, and git wins on conflict. Each adapter writes only raw; one transform builds staged; the export writes bill YAML from staged; nothing writes curated except the loader from git. Postgres with JSONB was chosen over a document database: records stay documents, and the queries that matter (measures by jurisdiction and topic, votes by party across bills, effects across households, sources by role) are joins and aggregations. A document database was considered and would store the records just as well; it is weaker for those queries and for the SQL and Parquet access that researchers expect.

## Components

| Component | Kind | Reason for the cut |
| --- | --- | --- |
| `core` | library | schema loading, generated models, record IO, validation; shared by everything |
| `ingest_<jurisdiction>` | batch job | one adapter per parliament; the federal one uses the parliament filter API and detail JSON, states will differ and some will be manual |
| `documents` | batch job | fetch, archive, text extraction (pdftotext), chunking, index; shared by drafting and chat |
| `drafting` | batch job | LLM drafts of measure records with citation anchors, output as a pull request, never directly into `data/` |
| `simulation` | service | wrapper around EUROMOD: CLI, FastAPI and MCP; separate because of the .NET runtime and because results are cached |
| `publish` | batch job | turns records and results into the site's content and the export artifacts |
| `web` | static site | Astro with islands for the household switcher, "Mein Haushalt" (local computation, nothing stored) and visualizations |
| `api` | service | feedback intake, error flags, follow-up sign-ups, chat; owns the warehouse; Phase 4 |

Batch jobs run as scheduled GitHub Actions, as a CLI per step and in order; an orchestrator only when steps multiply across jurisdictions. Local development uses Docker Compose for Postgres, CI a Postgres service container, production a small VPS or a managed free tier until volumes matter. In Phase 1 the simulation runs locally and commits results; it becomes a hosted service when "Mein Haushalt" needs live calls.

## Data flow

```
parliament APIs, RIS, budget office PDFs
        |  ingest_*, documents
        v
   Postgres raw -> staged  (export) -> data/bills/*.yaml, archived documents
        |  drafting (LLM) -> pull request -> human review (release checklist)
        v
   data/measures/*.yaml
        |  simulation -> data/results/
        v
   publish -> web (static) + exports (Parquet, JSON)
                     ^
   api <- feedback, flags, sign-ups, chat   (summaries flow back into data/ as records)
```

Content flows one way, from sources through review into the site. User data flows the other way into the API and only aggregated summaries return as versioned records.

## Jurisdictions

`data/jurisdictions/<country>.yaml` registers every decision level of a country: the federal level and the states now, municipalities later. Each entry names the parliament, the law source, the gazette, the impact assessment and the budget analysis body at that level, and whether the level is active in the methodology. Austria: law texts for all levels are uniform through RIS; the Landtage have no common interface and will need individual adapters or manual intake. States are inactive until the five federal cards exist.

Households are national archetypes. A state-specific measure affects a household through its region field; the record says which states the measure applies to.

## Plain language for bills

The site leads with what a bill does, not its legal name. Sources, in order: the heading of the section about the bill inside a Parlamentskorrespondenz release (fetched by `ingest-at press` into `raw.document`, extracted into `staged.press_section`), the Kurzinformation of the parliament administration, the official title. Every headline names its source. Bills are grouped into areas of life mapped from the parliament's own topics, and the tracker opens on what is upcoming, recently decided and newly introduced. Stage descriptions are plain sentences with durations, computed in the publish step against the data date. Each bill has its own page with summary, path, vote, relation to EU law, press reports and documents.

## Relation to EU law

Every bill carries `eu_relation`: whether it transposes an EU directive, contains accompanying rules for a directly applicable EU regulation, lies within EU law without being required by it, or is outside EU law. The source is the standard section "Verhältnis zu den Rechtsvorschriften der Europäischen Union" of the impact assessment, which decides the kind; transposition wording and CELEX numbers in the law text and explanations add the EU acts, and decide the kind only when no impact assessment exists. Acts link to EUR-Lex by CELEX number and carry their EU ELI. The impact assessment's statement that a bill goes beyond what EU law requires is kept as its own flag. The step is `ingest-at eu`, writing `staged.bill_eu`; the export marks the result as unchecked text extraction until a human sets `checked: true` on the bill record, after which the curated value is kept. Omnibus bills often mix kinds; the site then shows "teilweise". Per-measure EU relations and Austria's votes at EU level are later steps.

## Identifiers

| What | Identifier | Where it comes from |
| --- | --- | --- |
| Jurisdiction | ISO 3166-1 alpha-2, ISO 3166-2 for states | fixed |
| Published act | ELI as URL | RIS, `https://www.ris.bka.gv.at/eli/bgbl/I/<year>/<number>` |
| EU act | CELEX number, EU ELI | extracted from the bill's documents, linked to EUR-Lex |
| Bill | jurisdiction plus the parliament's own key | parliament API |
| Topic | EuroVoc descriptor | parliament API |
| Party, politician | Wikidata id | Wikidata |
| Source | repo-local id plus URL, retrieval date, archive link | editorial |

## Data access

- **Files**: `data/` in the repository, CC BY 4.0.
- **Exports**: `publish` writes Parquet and JSON per record kind with a version tag; releases get a DOI once the dataset is cited.
- **REST**: FastAPI with OpenAPI generated from Pydantic models that are generated from the JSON Schema. Read endpoints are public; write endpoints exist only for feedback.
- **MCP**: an MCP server built on the same models. Every tool result includes label, assumptions and source references, so an assistant cannot quote a number without its caveats.

## Editions

An edition is a configuration file in the site, `web/editions/at.json`: jurisdiction codes it covers, default language, the local names of chambers and stages, theme tokens, enabled features (tracker, cards, Mein Haushalt, chat), legal pages and the correction contact. The Austrian edition is published under the marketing name Durchgerechnet. A new country is a new edition plus a new ingest adapter plus a methodology appendix, never a fork of the site.

## Frontend

Astro, static output, Svelte islands, pnpm, deployed to GitHub Pages by a manually triggered workflow that leaves out unapproved cards unless asked. Fonts are self-hosted through Fontsource, so the site loads nothing from third parties. Content collections validate the records at build time with a schema derived from `schema/massnahme.schema.json`; a broken record fails the build. Routes are per jurisdiction and language. Islands in Svelte or Preact for the household switcher, "Mein Haushalt" and charts. Explorer views that outgrow pregenerated JSON read the API.

## Repository layout (target)

```
schema/           JSON Schema, generated Pydantic models, generated TypeScript types
data/
  jurisdictions/  AT.yaml
  households/     AT.yaml
  bills/          AT-XXVIII-I-69.yaml
  measures/       at-2025-klimabonus.yaml
  results/        simulation outputs
services/
  core/  ingest_at/  documents/  drafting/  simulation/  publish/  api/
web/              Astro
evals/            style and faithfulness cases from the Stilguide, run on prompt changes
fixtures/         real API responses and PDFs from the spike, for tests without network
.github/workflows CI (validate, build) and scheduled ingest
```

Tooling: uv workspace with one `pyproject.toml` per service, ruff, pytest, pyright. Models are generated from the schema, never written by hand.

## Record kinds planned

- `party_position`: a sourced quote from a programme or manifesto, linked to a measure and to the vote on it. Never a score. First source: the Manifesto Project.
- `result`: a simulation output with model version, input file and household.
- `follow_up`: what actually happened one year later, with sources.

## Open decisions

- Simulation hosting: local runs with committed results until live calls are needed.
- Island framework: Svelte or Preact.
