# AI Support Ticket Triage API

> A reliable FastAPI workflow that turns incoming support tickets into validated, structured triage decisions—with deterministic fallbacks when an AI provider is unavailable.

**Status:** Under active development. Stage 0 provides the executable FastAPI application shell, typed settings, health endpoint, quality tooling, and CI. Ticket-domain and triage endpoints remain planned for later stages.

## The problem

Support teams receive a growing volume of messages that need consistent categorisation, prioritisation, and safe first responses. A generic chatbot is not enough: the output must be structured, validated, persisted, and safe to hand to a human workflow.

This service receives a ticket and produces a decision such as:

```json
{
  "category": "refund",
  "priority": "high",
  "sentiment": "frustrated",
  "needs_human_review": true,
  "suggested_reply": "I’m sorry this has been frustrating. A support specialist will review your refund request shortly.",
  "provenance": "fallback"
}
```

The suggested reply is always a **draft**. The service does not send messages to customers or take autonomous actions.

## Key features

- Create, store, retrieve, and filter support tickets
- Structured triage: category, priority, sentiment, human-review flag, and reply draft
- Deterministic rule-based triage that works without a model, API key, or network
- Configurable Fake provider for repeatable local demos and automated tests
- Optional Ollama and OpenAI-compatible adapters behind one provider contract
- Strict validation of untrusted model output before it reaches business state
- Safe fallback when a provider times out, fails, or returns malformed output
- SQLite-first local development with PostgreSQL compatibility
- FastAPI/OpenAPI, Docker Compose, Ruff, Pyright, pytest, and CI

## Why it is useful as a reference project

This is intentionally an operational AI component—not an unbounded agent demo. It shows the engineering decisions businesses need when integrating AI into an existing workflow:

| Concern | Approach |
| --- | --- |
| Reliability | Deterministic fallback and explicit decision provenance |
| Safety | Model output is validated; ambiguous cases route to human review |
| Testability | Fake and scripted providers; normal tests need no model/API key |
| Maintainability | Clean Architecture and dependency injection |
| Data | Persisted ticket and triage lifecycle, query filters, and migrations |
| Delivery | Docker, automated checks, typed configuration, documented API |

## Planned workflow

```text
POST /tickets
    │
    ▼
Validate input → create ticket → request triage decision
                                      │
                         AI provider ─┴─ rule-based fallback
                                      │
                                      ▼
                     validate decision → persist → return response
```

A provider may help understand the message, but it never controls persistence rules, output schema, or customer communication.

## Technology stack

- Python 3.12
- FastAPI and Uvicorn
- Async SQLAlchemy and Alembic
- SQLite for simple local usage; PostgreSQL-compatible repository contract
- `uv` for dependency management
- Ollama / OpenAI-compatible APIs as optional adapters
- Docker and Docker Compose
- pytest, HTTPX, Ruff, Pyright, and pytest-cov

## Architecture

```text
src/ai_ticket_triage/
├── domain/             # Ticket, decision, policies, domain errors
├── application/        # use cases, ports, DTOs
├── infrastructure/     # database and provider adapters, settings
├── presentation/       # FastAPI routes, HTTP mapping, error handlers
└── composition_root/   # dependency wiring and application factory
```

The domain and application layers do not import FastAPI, SQLAlchemy, or provider SDK types. Provider-specific configuration and HTTP clients remain in infrastructure adapters.

## Prerequisites

For the planned v1 release:

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker with Docker Compose (optional; recommended for PostgreSQL)

## Installation

### Local development with the Fake provider

The Fake provider is the default local path. It enables an end-to-end workflow without Ollama, an OpenAI key, or internet access.

```bash
git clone https://github.com/hamresan/ai-ticket-triage-api.git
cd ai-ticket-triage-api

cp .env.example .env
uv sync
uv run alembic upgrade head
uv run uvicorn ai_ticket_triage.presentation.app:create_app --factory --reload
```

Open:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

### Docker Compose

Once the release hardening stage adds the verified Compose setup:

```bash
git clone https://github.com/hamresan/ai-ticket-triage-api.git
cd ai-ticket-triage-api

cp .env.example .env
docker compose up --build
```

## Configuration

The planned environment contract keeps AI optional:

```dotenv
# fake (default), ollama, or openai_compatible
TRIAGE_PROVIDER=fake

# Simple local database
DATABASE_URL=sqlite+aiosqlite:///./ai_ticket_triage.db

# Used only when TRIAGE_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434/v1
OLLAMA_MODEL=qwen3:8b
PROVIDER_TIMEOUT_SECONDS=20

# Used only when TRIAGE_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=https://your-provider.example/v1
OPENAI_COMPATIBLE_API_KEY=
OPENAI_COMPATIBLE_MODEL=
```

Never commit a real API key. The default test suite and Fake-provider workflow must remain fully functional without any credentials.

## Quick start

After the API is implemented and running, create a ticket:

```bash
curl --request POST "http://localhost:8000/tickets" \
  --header "Content-Type: application/json" \
  --data '{
    "subject": "Refund request for my duplicate charge",
    "message": "I was charged twice and need help getting the duplicate payment refunded.",
    "customer_reference": "cust_123"
  }'
```

Expected v1 response:

```json
{
  "ticket_id": "tk_01JQ8T31VH4P",
  "status": "triaged",
  "subject": "Refund request for my duplicate charge",
  "decision": {
    "category": "refund",
    "priority": "high",
    "sentiment": "frustrated",
    "needs_human_review": true,
    "suggested_reply": "I’m sorry about the duplicate charge. A support specialist will review the refund request.",
    "provenance": "fallback"
  }
}
```

Retrieve the result later:

```bash
curl "http://localhost:8000/tickets/tk_01JQ8T31VH4P"
```

Filter tickets needing a human:

```bash
curl "http://localhost:8000/tickets?needs_human_review=true&priority=high&limit=20"
```

## Planned API

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/tickets` | Create, triage, and persist a support ticket |
| `GET` | `/tickets/{ticket_id}` | Retrieve one ticket and its triage decision |
| `GET` | `/tickets` | Filter by status, category, priority, or review flag |
| `GET` | `/health` | Health check for local and container use |

The public response deliberately contains a validated decision, not an opaque raw model response.

## Triage policy

The initial categories are:

- `refund`
- `billing`
- `account_access`
- `technical_issue`
- `abuse`
- `unknown`

Rule-based fallback is conservative. If a message is ambiguous, incomplete, unsafe, or does not match a reliable category, it is marked `needs_human_review: true` rather than given false confidence.

Provider results are rejected and replaced by fallback when they contain invalid JSON, unknown enums, invalid/oversized fields, unsafe reply shapes, or a provider timeout/error.

## Development and testing

Once the foundation stage is completed, run the full quality gate:

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright src tests
uv run pytest --cov=ai_ticket_triage --cov-branch --cov-report=term-missing
```

The test suite is designed around real behaviour:

- **Unit tests** cover domain policies, decision validation, fallbacks, prompts, mappers, and factories.
- **Integration tests** use a real temporary SQLite database and async SQLAlchemy repositories.
- **API tests** exercise the real FastAPI application and request/response schemas.
- **Provider tests** use Fake/scripted transports; a live Ollama server or external API is never required for normal tests.

Quality targets are at least **85% branch coverage** overall and **90% branch coverage** in domain/application code. Coverage is a floor; meaningful tests for validation, failures, provider errors, and persistence are required.

## Roadmap

Development is split into individually reviewed branches:

1. Foundation and executable application shell
2. Domain model and application contracts
3. SQLite persistence and basic ticket API
4. Deterministic triage, Fake provider, and fallback
5. Structured Ollama adapter and validated output
6. OpenAI-compatible adapter and explicit provider selection
7. Reliability, idempotency, filtering, and API error policy
8. Release hardening, documentation, Docker, and public repository hygiene

Each stage is developed on a dedicated branch and merges only after Ruff, formatting, Pyright, tests, branch coverage, and CI pass.

## Safety and privacy notes

- Do not log ticket text, full prompts, credentials, or raw provider responses by default.
- Treat provider output as untrusted data and validate it before persistence.
- A draft reply must not be sent automatically to a customer.
- Apply authentication, authorization, rate limiting, and retention rules before using this service with real support data.
- Prefer a local/Fake provider for demos and tests that do not require a live model.

## Scope and non-goals for v1

The first version deliberately excludes:

- Sending replies, email/CRM/helpdesk integrations
- Authentication and multi-tenancy
- RAG/knowledge-base retrieval
- Background queues and analytics dashboards
- A frontend
- Autonomous support agents

These are sensible future extensions, but are out of scope so the core triage behaviour remains clear, safe, and thoroughly testable.

## Contributing

Contributions are welcome once the implementation is available. Keep changes focused, follow the package boundaries, add mirrored behavioural tests, run the quality checks, and never commit customer data or credentials.

## License

This project will be released under the [MIT License](./LICENSE).
