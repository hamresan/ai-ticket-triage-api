import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

import httpx
import pytest
from alembic import command
from alembic.config import Config

from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.application.tickets.policies import TicketRequestFingerprint
from ai_ticket_triage.application.tickets.use_cases import CreateTicket
from ai_ticket_triage.application.triage.dto import TriageTicketInput
from ai_ticket_triage.application.triage.use_cases import TriageTicket
from ai_ticket_triage.domain.tickets import TicketStatus
from ai_ticket_triage.domain.triage import Category, TriageProvenance
from ai_ticket_triage.domain.triage.policies import (
    DeterministicTriagePolicy,
    FallbackDecisionCatalog,
    TriageSignalDetector,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.database import (
    create_engine,
    create_session_factory,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyTicketRepository,
)
from ai_ticket_triage.infrastructure.providers.ollama import OllamaTriageProvider
from ai_ticket_triage.infrastructure.providers.structured import (
    StructuredTriageResponseMapper,
    TriagePromptBuilder,
)
from ai_ticket_triage.infrastructure.providers.structured.parser import (
    StructuredTriageOutputParser,
)
from ai_ticket_triage.infrastructure.providers.structured.validator import (
    StructuredTriageOutputValidator,
)
from ai_ticket_triage.infrastructure.providers.transport import HttpxOllamaTransport


def test_ollama_timeout_persists_fallback_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'fallback.db'}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config("alembic.ini"), "head")

    async def exercise() -> None:
        engine = create_engine(database_url)
        repository = SqlAlchemyTicketRepository(create_session_factory(engine))
        now = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
        ticket_id = UUID("00000000-0000-0000-0000-000000000403")
        create = CreateTicket(
            repository, lambda: ticket_id, lambda: now, TicketRequestFingerprint()
        )

        def timeout_handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("scripted timeout", request=request)

        provider = OllamaTriageProvider(
            model="test-model",
            transport=HttpxOllamaTransport(
                base_url="http://ollama.test",
                timeout_seconds=1.0,
                http_transport=httpx.MockTransport(timeout_handler),
            ),
            prompt_builder=TriagePromptBuilder(),
            response_mapper=StructuredTriageResponseMapper(
                StructuredTriageOutputParser(StructuredTriageOutputValidator())
            ),
        )
        triage = TriageTicket(
            repository,
            provider,
            DeterministicTriagePolicy(
                TriageSignalDetector.default(), FallbackDecisionCatalog.default()
            ),
            lambda: now + timedelta(seconds=1),
        )
        creation = await create.execute(
            CreateTicketInput(
                subject="Refund request",
                message="Please refund my order.",
                idempotency_key="ollama-fallback",
            )
        )
        result = await triage.execute(TriageTicketInput(creation.ticket.id))
        persisted = await repository.get_by_id(creation.ticket.id)

        assert result.status is TicketStatus.TRIAGED
        assert result.decision is not None
        assert result.decision.category is Category.REFUND
        assert result.decision.provenance is TriageProvenance.FALLBACK
        assert persisted == result
        await engine.dispose()

    asyncio.run(exercise())
