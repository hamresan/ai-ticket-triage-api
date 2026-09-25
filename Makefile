.PHONY: check lint format-check type-check test run up down logs migrate

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

up:
	docker compose up --build --detach

down:
	docker compose down

logs:
	docker compose logs --follow api

migrate:
	docker compose run --rm api alembic upgrade head
