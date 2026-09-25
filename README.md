# AI Support Ticket Triage API

[![Quality](https://github.com/hamresan/ai-ticket-triage-api/actions/workflows/quality.yml/badge.svg)](https://github.com/hamresan/ai-ticket-triage-api/actions/workflows/quality.yml)

A production-oriented FastAPI reference service that turns support tickets into validated, persisted triage decisions with deterministic fallback when an AI provider is unavailable.

The service creates, triages, retrieves, and filters tickets. Suggested replies are **drafts only**; this project never sends customer messages automatically.

## What it demonstrates

- Clean Architecture with framework-free domain/application layers
- Async SQLAlchemy persistence and Alembic migrations
- Deterministic Fake provider requiring no model, credential, or network
- Optional Ollama and OpenAI-compatible provider adapters
- Strict validation of untrusted provider output
- Deterministic fallback and explicit decision provenance
- Database-backed idempotent ticket creation, including concurrent duplicates
- Deterministic filtering, ordering, and pagination
- Safe centralized API errors with request IDs
- Structured operational logging without ticket text, prompts, credentials, idempotency keys, or raw provider output
- Ruff, strict Pyright, pytest branch coverage, OpenAPI contract checks, Docker smoke tests, and GitHub Actions CI

## Architecture

```text
src/ai_ticket_triage/
├── domain/             # entities, value objects, domain policies/errors
├── application/        # use cases, DTOs, ports, application policies
├── infrastructure/     # SQLAlchemy and AI-provider adapters, settings
├── presentation/       # FastAPI routes, schemas, mappers, middleware/errors
└── composition_root/   # explicit dependency wiring
```

The domain and application layers do not import FastAPI, SQLAlchemy, or provider SDK types. Provider-specific transport and configuration stay in infrastructure.

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- Docker (optional, only for the container workflow)

## Quick start — SQLite + Fake provider

The default configuration is the simplest path and needs no external AI access.

```bash
git clone https://github.com/hamresan/ai-ticket-triage-api.git
cd ai-ticket-triage-api
cp .env.example .env

uv sync --locked
uv run alembic upgrade head
uv run uvicorn ai_ticket_triage.presentation.app:create_app --factory --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
curl --fail http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Create and triage a ticket

`Idempotency-Key` is required and must contain 1–255 characters.

```bash
curl --request POST "http://127.0.0.1:8000/api/v1/tickets" \
  --header "Content-Type: application/json" \
  --header "Idempotency-Key: demo-ticket-001" \
  --data '{
    "subject": "Cannot sign in",
    "message": "The login page keeps returning an error."
  }'
```

The first accepted request returns HTTP `201`. With the default Fake provider, the response has this shape (UUID and timestamps vary):

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "subject": "Cannot sign in",
  "message": "The login page keeps returning an error.",
  "status": "triaged",
  "created_at": "2026-09-25T12:00:00Z",
  "updated_at": "2026-09-25T12:00:00Z",
  "decision": {
    "category": "technical",
    "priority": "medium",
    "sentiment": "neutral",
    "needs_human_review": false,
    "suggested_reply": "This is a draft response from the Fake triage provider.",
    "provenance": "provider"
  }
}
```

Replay the same key with the same subject/message to receive the persisted ticket with HTTP `200` and no repeated triage. Reuse the key with a different payload and the API returns HTTP `409`:

```json
{
  "error": {
    "code": "idempotency_conflict",
    "message": "Idempotency key was already used for a different request."
  },
  "request_id": "request-id"
}
```

The `request_id` is also returned in the `X-Request-ID` response header.

## Retrieve and query tickets

Retrieve one ticket:

```bash
curl "http://127.0.0.1:8000/api/v1/tickets/<ticket-id>"
```

List tickets:

```bash
curl "http://127.0.0.1:8000/api/v1/tickets"
```

Filter and paginate:

```bash
curl "http://127.0.0.1:8000/api/v1/tickets?status=triaged&category=technical&priority=medium&needs_human_review=false&offset=0&limit=50"
```

Supported filters are `status`, `category`, `priority`, and `needs_human_review`. Results are ordered by creation time and ticket ID. `offset` defaults to 0 and must be non-negative; `limit` defaults to 50 and must be between 1 and 100.

## API

| Method | Endpoint | Behavior |
| --- | --- | --- |
| `GET` | `/health` | Process health check |
| `POST` | `/api/v1/tickets` | Idempotently create, triage, persist, and return a ticket |
| `GET` | `/api/v1/tickets/{ticket_id}` | Retrieve one ticket or return `ticket_not_found` |
| `GET` | `/api/v1/tickets` | Deterministically filter, order, and paginate tickets |

FastAPI serves the generated OpenAPI document at `/openapi.json`. CI contract tests verify that the documented public paths, required idempotency header, filters, and response models remain present.

## Configuration

The default `.env.example` uses SQLite and the Fake provider:

```dotenv
APP_NAME="AI Support Ticket Triage API"
APP_ENV=local
DATABASE_URL=sqlite+aiosqlite:///./ai_ticket_triage.db
TRIAGE_PROVIDER=fake
PROVIDER_MODEL=
PROVIDER_BASE_URL=
PROVIDER_TIMEOUT_SECONDS=10
PROVIDER_API_KEY=
```

### Ollama

```dotenv
TRIAGE_PROVIDER=ollama
PROVIDER_MODEL=qwen3:8b
PROVIDER_BASE_URL=http://localhost:11434
PROVIDER_TIMEOUT_SECONDS=20
```

Ollama uses its native `/api/chat` endpoint.

### OpenAI-compatible endpoint

```dotenv
TRIAGE_PROVIDER=openai_compatible
PROVIDER_MODEL=your-model-name
PROVIDER_BASE_URL=https://your-provider.example/v1
PROVIDER_TIMEOUT_SECONDS=20
PROVIDER_API_KEY=
```

The adapter calls `/chat/completions` relative to `PROVIDER_BASE_URL`. `PROVIDER_API_KEY` is optional and, when present, is sent as bearer authentication. Never commit real credentials.

All providers feed the same versioned triage task and strict structured-output validation pipeline. Recoverable provider failures use deterministic fallback.

## Docker

The repository includes a tested application image and a Docker Compose configuration using SQLite + the Fake provider. No PostgreSQL Compose setup is advertised because a PostgreSQL path is not currently shipped and CI-verified.

### Docker Compose

Start the complete local stack:

```bash
docker compose up --build
```

The Compose service runs Alembic migrations before starting the API, publishes port `8000`, persists SQLite data in the `ticket_data` named volume, and includes an application health check. No external AI service or credential is required.

Verify it:

```bash
curl --fail http://127.0.0.1:8000/health
```

Stop the service while keeping its data:

```bash
docker compose down
```

Remove the service and its persisted local database:

```bash
docker compose down --volumes
```

### Docker image

Build:

```bash
docker build -t ai-ticket-triage .
```

Run migrations and the API in one container:

```bash
docker run --rm --name ai-ticket-triage \
  -p 8000:8000 \
  ai-ticket-triage \
  sh -c 'alembic upgrade head && exec uvicorn ai_ticket_triage.presentation.app:create_app --factory --host 0.0.0.0 --port 8000'
```

Then use the same health/create/query commands shown above. Direct `docker run` data is ephemeral unless you provide persistent storage and an appropriate `DATABASE_URL`; the Compose configuration already provides a persistent SQLite volume.

## Development checks

Run the complete local quality gate:

```bash
make check
```

Equivalent commands:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright src tests
uv run pytest --cov=ai_ticket_triage --cov-branch --cov-report=term-missing
```

Overall branch coverage must remain at least 85%. Tests are behavioral: unit tests cover domain/application/provider boundaries; integration tests use real temporary SQLite databases and Alembic; API tests exercise the real FastAPI application. Normal tests never require a live AI provider.

## Safety, privacy, and known limitations

- Ticket text and provider prompts may contain sensitive data. Normal structured request logs intentionally exclude them.
- Provider output is untrusted and validated before persistence.
- Suggested replies are drafts and are never sent automatically.
- Authentication, authorization, multi-tenancy, rate limiting, retention/deletion workflows, background queues, CRM/helpdesk integration, RAG, analytics dashboards, and a frontend are outside this reference service.
- The included Docker release path uses SQLite. PostgreSQL is not documented as a supported release path until its driver, migrations, Compose configuration, and CI verification are shipped together.
- Before internet-facing production use, add deployment-specific security and operational controls described in [SECURITY.md](./SECURITY.md).

## Repository documentation

- [Implementation roadmap](./docs/implementation-roadmap.md)
- [Release checklist](./docs/release-checklist.md)
- [Security policy](./SECURITY.md)
- [MIT License](./LICENSE)

## Contributing

Keep changes focused, preserve package boundaries, add mirrored behavioral tests, run `make check`, and never commit credentials or customer data.

## License

MIT.
