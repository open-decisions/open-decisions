.PHONY: setup db lint format typecheck test validate check ingest documents

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
