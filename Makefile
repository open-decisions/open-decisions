.PHONY: setup db lint format typecheck test validate check ingest documents render site site-dev site-test

setup:
	uv sync
	uv run pre-commit install

db:
	docker compose up -d db
	uv run open-decisions-migrate

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff check --fix .
	uv run ruff format .

typecheck:
	uv run pyright

test:
	uv run pytest

validate:
	uv run open-decisions-validate

check: lint typecheck test validate

ingest:
	uv run ingest-at run

documents:
	uv run documents run

render:
	uv run publish render

site:
	uv run publish site
	cd web && pnpm install --frozen-lockfile && pnpm check && pnpm build

site-dev:
	uv run publish site
	cd web && SHOW_DRAFTS=true pnpm dev

site-test:
	uv run publish site
	cd web && SHOW_DRAFTS=true pnpm build && pnpm test
