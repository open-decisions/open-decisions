# Architecture

Status: target architecture, October 2026. Nothing below is built yet except the schema, the records and the validator. German concept documents live next to this file; this document is in English because it describes code.

## Principles

1. **The curated record is the product.** A decision, its measured effect per household type, the official message next to the law, and who voted for it, in one schema, with a label on every number and a source on every statement. Raw open data already exists elsewhere; the curated, linked, reviewed record does not.
2. **Boundaries without network calls where possible.** Components are separate packages with explicit contracts and their own tests, which is what humans and AI agents work well on. A component becomes a running service only when it has a different runtime, a different cost profile, or different data sensitivity.
3. **Git is the content database.** Records are YAML files reviewed in pull requests. Versioning, public corrections, the changelog per card and "all assumptions versioned" come for free. Everything users send and everything ingested in bulk goes elsewhere.
4. **One schema, several surfaces.** Files, bulk exports, a REST API and an MCP server all serve the same records. The label and the sources travel with every number on every surface.
5. **Link, don't invent.** Laws carry their ELI, topics their EuroVoc descriptors, parties and people their Wikidata ids. Jurisdictions use ISO 3166 codes. This is what makes records comparable across levels and later across countries.
6. **Content in the language of the jurisdiction, code in English.** Sources and readers are local. The contract is not.

## Layers

| Layer | Store | Content | Exists |
| --- | --- | --- | --- |
| Records | git, `data/` | jurisdictions, households, bills, measures; later party positions | yes |
| Results | git, `data/results/` | simulation outputs, cached and versioned | planned, Phase 1 |
| Warehouse | Postgres | everything ingested from parliaments and document stores, extracted text, embeddings, user feedback, chat cache | planned, Phase 4 or second country |
| Exports | release artifacts | the public dataset as Parquet and JSON, versioned, later with a DOI | planned, Phase 3 |
| API | FastAPI | read access to records and results, write access for feedback | planned, Phase 4 |
| MCP | MCP server on the same models | tools for assistants: search measures, get measure, get bill, household effect, list sources | planned, Phase 4 |
| Site | Astro, static output | cards, detail pages, methodology, corrections, tracker; interactive islands | planned, Phase 1 |

The warehouse decision is open. Postgres with JSONB is the working assumption: records stay documents, and the queries that matter (measures by jurisdiction and topic, votes by party across bills, effects across households, sources by role) are joins and aggregations. A document database was considered and would store the records just as well; it is weaker for those queries and for the SQL and Parquet access that researchers expect.

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

Batch jobs run as scheduled GitHub Actions. In Phase 1 the simulation runs locally and commits results; it becomes a hosted service when "Mein Haushalt" needs live calls.

## Data flow

```
parliament APIs, RIS, budget office PDFs
        |  ingest_*, documents
        v
   data/bills/*.yaml  +  archived documents
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

## Identifiers

| What | Identifier | Where it comes from |
| --- | --- | --- |
| Jurisdiction | ISO 3166-1 alpha-2, ISO 3166-2 for states | fixed |
| Published act | ELI as URL | RIS, `https://www.ris.bka.gv.at/eli/bgbl/I/<year>/<number>` |
| Bill | jurisdiction plus the parliament's own key | parliament API |
| Topic | EuroVoc descriptor | parliament API |
| Party, politician | Wikidata id | Wikidata |
| Source | repo-local id plus URL, retrieval date, archive link | editorial |

## Data access

- **Files**: `data/` in the repository, CC BY 4.0.
- **Exports**: `publish` writes Parquet and JSON per record kind with a version tag; releases get a DOI once the dataset is cited.
- **REST**: FastAPI with OpenAPI generated from Pydantic models that are generated from the JSON Schema. Read endpoints are public; write endpoints exist only for feedback.
- **MCP**: an MCP server built on the same models. Every tool result includes label, assumptions and source references, so an assistant cannot quote a number without its caveats.

## Frontend

Astro, static output, deployed to Cloudflare Pages or GitHub Pages. Content collections validate the records at build time with a schema derived from `schema/massnahme.schema.json`; a broken record fails the build. Routes are per jurisdiction and language. Islands in Svelte or Preact for the household switcher, "Mein Haushalt" and charts. Explorer views that outgrow pregenerated JSON read the API.

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

- Warehouse: Postgres with JSONB (working assumption) or a document database. Decide when the second country or the explorer needs it.
- Simulation hosting: local runs with committed results until live calls are needed.
- Island framework: Svelte or Preact.
