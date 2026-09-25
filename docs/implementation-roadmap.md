# Implementation roadmap

This document records the architecture delivered through the public-release hardening stage. The detailed planning source remains the reviewed implementation roadmap; this repository copy records the accepted outcomes that are now represented by code and tests.

## Foundation

Delivered the Python 3.12 `src/` package, typed settings, application factory, `/health`, MIT license, Makefile, Ruff, strict Pyright, pytest/coverage, Alembic, and GitHub Actions quality gate.

## Stage 1 — Domain model and application contracts

Delivered immutable ticket and triage domain concepts, bounded validation, explicit status ownership, repository/provider ports, and framework-free application DTOs. Domain/application APIs do not depend on FastAPI, SQLAlchemy, or provider SDK types.

## Stage 2 — Persistence and basic ticket API

Delivered async SQLAlchemy persistence, Alembic migrations, SQLite local configuration, repository adapters, and FastAPI create/retrieve/list endpoints with presentation-layer mapping and deterministic errors.

## Stage 3 — Deterministic triage, Fake provider, and fallback

Delivered the `TriageTicket` use case, deterministic conservative fallback policy, deterministic Fake provider, persisted provenance, and draft-only suggested replies. The default workflow needs no model, API key, or network access.

## Stage 4 — Structured AI-provider contract and Ollama adapter

Delivered versioned triage task schemas, prompt builder, strict structured-output mapper/validator, typed provider settings, Ollama transport/adapter, provider failure mapping, and deterministic fallback. Provider construction remains explicit at the infrastructure/composition boundary.

## Stage 5 — OpenAI-compatible adapter and provider selection

Delivered an OpenAI-compatible chat-completions adapter using the same application contract and structured validation pipeline. Provider selection is configuration-driven across Fake, Ollama, and OpenAI-compatible implementations without changing the triage use case.

## Stage 6 — Reliability, idempotency, query semantics, and API error policy

Delivered caller-supplied `Idempotency-Key`, database-enforced idempotency records, transaction-safe sequential/concurrent replay behavior, deterministic list filters/order/pagination, centralized safe HTTP errors with request IDs, and lightweight structured operational logging that excludes sensitive ticket/provider content.

Accepted idempotency behavior:

- first key + payload: create and triage, HTTP 201;
- same key + same payload: return the persisted ticket without repeating triage, HTTP 200;
- same key + different payload: reject with `idempotency_conflict`, HTTP 409.

## Stage 7 — Public release hardening and documentation

Delivered a verified Fake-provider local walkthrough, complete request/response examples, tested Docker image, clean-clone CI verification, OpenAPI contract verification, security/limitations documentation, release checklist, package/repository hygiene review, and documentation aligned to implemented behavior.

SQLite remains the simplest local path. A PostgreSQL Docker Compose stack is intentionally **not** published in this stage because the project does not currently ship the async PostgreSQL driver or a CI-verified Compose path. This follows the roadmap rule that Compose is documented only when it is genuinely runnable and tested.

## Architecture constraints retained

- Domain and application layers stay framework/provider independent.
- External AI providers implement the application provider contract behind infrastructure adapters.
- Mapping and validation responsibilities remain outside use-case orchestration.
- Persistence invariants are enforced in the repository/database boundary.
- Dependencies are wired explicitly in the composition root; no service locator is used.
- Fake/scripted providers are the default test mechanism; normal CI makes no live AI calls.
- Suggested replies are drafts only.
