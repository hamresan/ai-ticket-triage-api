# AI Support Ticket Triage API — Implementation Roadmap

## Purpose

Build a public, production-quality FastAPI service that receives a customer-support ticket, persists it, and returns a validated triage decision:

```json
{
  "category": "refund",
  "priority": "high",
  "sentiment": "frustrated",
  "needs_human_review": true,
  "suggested_reply": "..."
}
```

The service is an operational workflow component, not a generic chatbot. A ticket must remain usable when an LLM is unavailable, malformed, slow, or returns an unsafe/unstructured result.

## Scope and boundaries

### In scope

- `POST /tickets` to create, triage, and persist a ticket.
- `GET /tickets/{ticket_id}` and filtered ticket listing.
- Triage fields: category, priority, sentiment, needs-human-review, and a suggested reply.
- Fake provider for deterministic local development and tests.
- Deterministic rule-based fallback.
- Ollama and OpenAI-compatible provider adapters behind a common contract.
- SQLite for local development and PostgreSQL compatibility through the same repository contract.

### Explicitly out of scope for v1

- Sending replies to customers, email/CRM/helpdesk integrations, authentication/multi-tenancy, a frontend, RAG/knowledge base, background queues, analytics dashboards, and autonomous agent behavior.
- Storing full prompts, credentials, or raw provider responses in normal application logs.

## Non-negotiable engineering rules

- Use Python 3.12, `uv`, FastAPI, async SQLAlchemy, Ruff, strict Pyright, pytest, and pytest-cov.
- Apply Clean Architecture, SOLID, explicit contracts, constructor dependency injection, and narrow responsibilities.
- Keep FastAPI routes thin. They map HTTP input/output only and call application use cases.
- Keep provider SDK types and provider-specific settings inside infrastructure adapters/factories; they must not leak into domain or application code.
- Keep triage understanding and suggested-reply generation separate responsibilities, even if one provider can perform both in an initial call.
- Treat every provider response as untrusted input. Validate it before it affects domain state.
- Do not instantiate repositories, provider clients, or settings inside use-case methods.
- Avoid generic `utils`, broad service classes, speculative registries, and fake abstractions.
- Version prompt/structured-output contracts in source once provider integration starts.

## Test strategy and quality gates

### Mirrored test structure

```text
src/ai_ticket_triage/domain/...          -> tests/unit/domain/...
src/ai_ticket_triage/application/...     -> tests/unit/application/...
src/ai_ticket_triage/infrastructure/...  -> tests/integration/infrastructure/...
src/ai_ticket_triage/presentation/...    -> tests/integration/presentation/...
```

### Real behavioral tests

- Use a real temporary SQLite database and async SQLAlchemy repositories in integration tests.
- Use FastAPI's real application/test client and actual request/response schemas.
- Use the Fake provider and explicit scripted provider fakes for deterministic provider behavior; never require an API key, Ollama server, or internet access in the normal test suite.
- Unit-test domain policies, prompt builders, response mappers, validators, fallbacks, and factories independently.
- Test happy, validation, malformed-model-output, timeout/provider-error, configuration-error, persistence-error, and edge cases.
- Test that fallback results are persisted correctly and that provider failure cannot create duplicate tickets or corrupt ticket status.
- Require at least 85% branch coverage for the whole project and at least 90% branch coverage for domain and application packages. Coverage is a floor, not a replacement for meaningful cases.

### Mandatory checks after every stage

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pyright src tests
uv run pytest --cov=ai_ticket_triage --cov-branch --cov-report=term-missing
```

Once added, `make check` must run the same commands.

## Branch and merge workflow

1. Never implement directly on `main`.
2. Create exactly one branch for each stage using the prescribed branch name.
3. Implement only the declared stage scope. Future-stage work and unrelated refactors stay out of the branch.
4. Add production code and mirrored tests together.
5. Run every mandatory check and inspect coverage before creating the pull request.
6. Update README/roadmap whenever the public contract or a stage decision changes.
7. Merge only after all stage acceptance criteria and quality gates pass.
8. After merge, delete the stage branch, update local `main`, reread this roadmap, and branch from the updated `main` for the next incomplete stage.

## Target architecture

```text
src/ai_ticket_triage/
├── domain/             # Ticket, TriageDecision, policies, domain errors
├── application/        # use cases, repository/provider contracts, DTOs
├── infrastructure/     # SQLAlchemy repositories, provider adapters, settings
├── presentation/       # FastAPI routes, request/response mappers, error handlers
└── composition_root/   # dependency wiring and application factory
```

The core workflow is:

```text
HTTP request -> validate -> create ticket -> triage decision
-> validate/fallback -> persist -> HTTP response
```

## Stage 0 — Foundation and executable application shell

**Branch:** `stage-00-project-foundation`

### Scope

- Create `pyproject.toml`, Python 3.12 `src/` layout, `.gitignore`, MIT `LICENSE`, and `Makefile`.
- Configure Ruff, strict Pyright, pytest, pytest-cov, and GitHub Actions quality checks.
- Implement an application factory, typed settings boundary, `GET /health`, and a minimal composition root.
- Add Dockerfile/Docker Compose only if both run a real application; avoid placeholder service definitions.
- Update README commands to match the actual package name and paths.

### Acceptance criteria

- `uv sync`, `uv run uvicorn ai_ticket_triage.presentation.app:create_app --factory`, and `GET /health` succeed on a clean checkout.
- `make check` runs lint, format, types, tests, and coverage.
- Integration tests call the real health endpoint.

## Stage 1 — Domain model and application contracts

**Branch:** `stage-01-domain-contracts`

### Scope

- Define immutable domain/value objects for Ticket, TicketStatus, TriageDecision, Category, Priority, Sentiment, and triage provenance (`provider` or `fallback`).
- Define domain validation and errors for empty subject/message, invalid state changes, invalid enum values, and overly long bounded text fields.
- Define application ports for a ticket repository and triage provider.
- Define use-case input/output DTOs without FastAPI or SQLAlchemy types.
- Specify status ownership: `new`, `triaged`, and `failed`; do not add unsupported workflow states.

### Acceptance criteria

- Domain tests cover valid construction, every invalid value/state boundary, and immutable result behavior.
- Application contracts can be exercised with small in-memory fakes without infrastructure imports.
- No provider SDK, database, or HTTP type appears in domain/application public APIs.

## Stage 2 — Persistence and basic ticket API

**Branch:** `stage-02-ticket-persistence-api`

### Scope

- Implement SQLAlchemy persistence with a real SQLite configuration and migration strategy.
- Implement repository adapters for create, retrieve by ID, and filtered listing.
- Add `POST /tickets`, `GET /tickets/{ticket_id}`, and `GET /tickets` request/response mapping.
- Persist the input ticket initially as `new`; do not add LLM integration in this stage.
- Add clear HTTP errors for invalid request data and unknown ticket IDs.

### Acceptance criteria

- Integration tests use a real temporary SQLite database and FastAPI app wiring.
- Ticket fields survive a repository round-trip and filters behave deterministically.
- API tests cover create, retrieve, filter combinations, invalid request, and not-found cases.

## Stage 3 — Deterministic triage, Fake provider, and fallback

**Branch:** `stage-03-deterministic-triage`

### Scope

- Implement a deterministic rule-based triage policy for known signals such as refund, billing, account access, technical issue, abusive language, and unknown input.
- Implement a configurable Fake provider with deterministic outputs for local development and tests.
- Implement a `TriageTicket` use case that updates a ticket from `new` to `triaged` with decision provenance.
- Define conservative fallback behavior: unknown/ambiguous tickets must be marked for human review rather than confidently misclassified.
- Produce a suggested reply only as a draft; it must never be sent by the API.

### Acceptance criteria

- The system can fully create and triage a ticket with no model, API key, or network access.
- Tests cover every category/priority boundary, ambiguous requests, rule conflicts, and human-review rules.
- Fallback and Fake-provider outcomes are visibly distinct in persisted provenance/metadata.

## Stage 4 — Structured AI-provider contract and Ollama adapter

**Branch:** `stage-04-ollama-structured-triage`

### Scope

- Create versioned task input/output schemas and a dedicated prompt builder for ticket triage.
- Add a strict provider-response mapper and validator that rejects missing/unknown categories, invalid priority, invalid JSON, excessively long output, and unsafe suggested-reply shapes.
- Add typed provider settings: provider name, model, timeout, and optional credentials, with safe validation.
- Implement an Ollama OpenAI-compatible adapter behind the existing provider contract.
- Implement timeout/error mapping and deterministic fallback on provider failure or malformed response.
- Keep provider construction in one explicit factory/composition point; do not use a service locator.

### Acceptance criteria

- Normal tests use scripted HTTP/provider fakes, not a live Ollama server.
- Tests cover valid structured mapping, malformed JSON, schema mismatch, timeout, provider error, unsupported provider, and missing configuration.
- Any provider failure results in a persisted fallback decision and never leaves a ticket in an impossible state.

## Stage 5 — OpenAI-compatible adapter and provider selection

**Branch:** `stage-05-openai-compatible-provider`

### Scope

- Add an OpenAI-compatible adapter using the same task contract and output validation pipeline.
- Extend the existing factory/settings validation to select Fake, Ollama, or OpenAI-compatible provider explicitly.
- Keep `TriageTicket` and domain/application contracts unchanged.
- Add configuration documentation without committing credentials or showing real secrets.

### Acceptance criteria

- Provider selection is covered by tests for each supported choice and every invalid/missing setting.
- Adapter tests verify request mapping and response mapping with a controlled fake transport.
- No live provider call is required for CI or the default test suite.

## Stage 6 — Reliability, query semantics, and API error policy

**Branch:** `stage-06-reliability-query-api`

### Scope

- Define idempotency behavior for ticket creation using a caller-supplied request key or deterministic request fingerprint; select one approach and document it.
- Prevent duplicate creation/triage under sequential and concurrent requests using a transaction-safe repository policy.
- Finalize listing filters for status, category, priority, and `needs_human_review`, including pagination/limit validation.
- Add centralized FastAPI error handlers that map expected domain/application errors to stable HTTP responses without leaking provider/database details.
- Add safe structured observability metadata (provider, model, duration, fallback used) without ticket text, prompts, credentials, or raw outputs.

### Acceptance criteria

- Integration tests prove duplicate requests do not create duplicate tickets or repeat state changes.
- Filters, pagination limits, and bad query parameters have deterministic API behavior.
- Error responses are safe and useful; logs/tests confirm no secret or ticket body leakage in standard error paths.

## Stage 7 — Public release hardening and documentation

**Branch:** `stage-07-release-hardening`

### Scope

- Add complete example requests/responses and a verified local walkthrough.
- Update README to remove development-status wording only after commands and endpoints are genuinely implemented.
- Add Docker Compose for app plus PostgreSQL only if it is tested and documented; keep SQLite as the simple local path.
- Add GitHub Actions badges, a clean-clone verification, security notes, known limitations, and release checklist.
- Perform a final review of package metadata, license, test coverage, and public repository hygiene.

### Acceptance criteria

- A new user can clone the repository, use Fake provider locally, create/query tickets, and run all documented checks.
- Ollama/OpenAI-compatible configuration is documented but optional for the default workflow.
- All quality gates pass with the coverage floor met.
- README, OpenAPI, tests, examples, and implementation agree exactly.

## Definition of done for every stage

- All stated scope and acceptance criteria are complete; no placeholder implementation is presented as complete.
- Production code and mirrored tests are committed together.
- README and roadmap reflect any public-contract decision made in the stage.
- Ruff, formatting, Pyright, pytest, and coverage checks pass.
- The branch is reviewed and merged only after verification; the next stage starts from updated `main`.