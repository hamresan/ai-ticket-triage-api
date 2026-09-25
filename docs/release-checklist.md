# Release checklist

- [ ] `uv sync --locked` succeeds from a clean clone.
- [ ] `uv run alembic upgrade head` succeeds with the default SQLite configuration.
- [ ] `make check` passes: Ruff, formatting, strict Pyright, pytest, and branch coverage.
- [ ] The Fake-provider walkthrough can create, replay, retrieve, filter, and list tickets without external AI access.
- [ ] `docker build .` succeeds and the image passes the documented health/create/query smoke test.
- [ ] README commands, examples, environment variables, and endpoint descriptions match the implementation.
- [ ] OpenAPI contract tests pass.
- [ ] Alembic is at a single expected head and migrations upgrade a fresh database.
- [ ] `.env.example` contains placeholders only.
- [ ] No credentials, customer data, local databases, coverage output, or generated caches are tracked.
- [ ] `LICENSE`, `SECURITY.md`, package metadata, and repository links are current.
- [ ] CI is green on the release commit.
