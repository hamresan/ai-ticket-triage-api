.PHONY: check lint format-check type-check test run

check: lint format-check type-check test

lint:
	uv run ruff check src tests

format-check:
	uv run ruff format --check src tests

type-check:
	uv run pyright src tests

test:
	uv run pytest --cov=ai_ticket_triage --cov-branch --cov-report=term-missing

run:
	uv run uvicorn ai_ticket_triage.presentation.app:create_app --factory
