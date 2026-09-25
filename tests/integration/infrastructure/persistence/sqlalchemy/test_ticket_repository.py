import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import IntegrityError

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.errors import IdempotencyConflictError
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.database import (
    create_engine,
    create_session_factory,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models import TicketModel
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.repositories import (
    SqlAlchemyTicketRepository,
)


def migrate(database_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", database_url)
    command.upgrade(Config("alembic.ini"), "head")


def test_repository_round_trip_and_status_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'tickets.db'}"
    migrate(database_url, monkeypatch)

    async def exercise() -> None:
        engine = create_engine(database_url)
        repository = SqlAlchemyTicketRepository(create_session_factory(engine))
        now = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
        ticket = Ticket(
            id=UUID("00000000-0000-0000-0000-000000000101"),
            subject=TicketSubject("Billing"),
            message=TicketMessage("Duplicate charge"),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        await repository.add(ticket)
        assert await repository.get_by_id(ticket.id) == ticket
        assert await repository.list(TicketFilter()) == (ticket,)
        assert await repository.list(TicketFilter(status=TicketStatus.NEW)) == (ticket,)
        assert await repository.list(TicketFilter(status=TicketStatus.FAILED)) == ()
        await engine.dispose()

    asyncio.run(exercise())


def test_database_constraint_rejects_blank_subject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'constraints.db'}"
    migrate(database_url, monkeypatch)

    async def exercise() -> None:
        engine = create_engine(database_url)
        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            session.add(
                TicketModel(
                    id=UUID("00000000-0000-0000-0000-000000000102"),
                    subject=" ",
                    message="message",
                    status="new",
                    created_at=datetime(2026, 9, 24, tzinfo=UTC),
                    updated_at=datetime(2026, 9, 24, tzinfo=UTC),
                )
            )
            with pytest.raises(IntegrityError):
                await session.commit()
        await engine.dispose()

    asyncio.run(exercise())


def test_repository_persists_final_triage_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'triage.db'}"
    migrate(database_url, monkeypatch)

    async def exercise() -> None:
        engine = create_engine(database_url)
        repository = SqlAlchemyTicketRepository(create_session_factory(engine))
        now = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
        ticket = Ticket(
            id=UUID("00000000-0000-0000-0000-000000000303"),
            subject=TicketSubject("Refund"),
            message=TicketMessage("I need a refund."),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        await repository.add(ticket)
        decision = TriageDecision(
            category=Category.REFUND,
            priority=Priority.HIGH,
            sentiment=Sentiment.NEGATIVE,
            needs_human_review=False,
            suggested_reply=SuggestedReply("Refund draft."),
            provenance=TriageProvenance.FALLBACK,
        )
        triaged = ticket.mark_triaged(decision, updated_at=now)

        await repository.update(triaged)

        assert await repository.get_by_id(ticket.id) == triaged
        await engine.dispose()

    asyncio.run(exercise())


def test_database_rejects_triaged_status_without_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'invalid-triage.db'}"
    migrate(database_url, monkeypatch)

    async def exercise() -> None:
        engine = create_engine(database_url)
        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            session.add(
                TicketModel(
                    id=UUID("00000000-0000-0000-0000-000000000306"),
                    subject="Technical",
                    message="Not working.",
                    status="triaged",
                    created_at=datetime(2026, 9, 24, tzinfo=UTC),
                    updated_at=datetime(2026, 9, 24, tzinfo=UTC),
                )
            )
            with pytest.raises(IntegrityError):
                await session.commit()
        await engine.dispose()

    asyncio.run(exercise())


def test_repository_enforces_idempotency_for_sequential_and_concurrent_writes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'idempotency.db'}"
    migrate(database_url, monkeypatch)

    async def exercise() -> None:
        engine = create_engine(database_url)
        repository = SqlAlchemyTicketRepository(create_session_factory(engine))
        now = datetime(2026, 9, 25, 8, 0, tzinfo=UTC)

        def ticket(ticket_id: str) -> Ticket:
            return Ticket(
                id=UUID(ticket_id),
                subject=TicketSubject("Same request"),
                message=TicketMessage("Same body"),
                status=TicketStatus.NEW,
                created_at=now,
                updated_at=now,
            )

        first_ticket = ticket("00000000-0000-0000-0000-000000000601")
        replay_ticket = ticket("00000000-0000-0000-0000-000000000602")
        first = await repository.add_idempotent(first_ticket, "same-key", "fingerprint")
        replay = await repository.add_idempotent(replay_ticket, "same-key", "fingerprint")

        assert first.created is True
        assert replay.created is False
        assert replay.ticket.id == first.ticket.id

        with pytest.raises(IdempotencyConflictError):
            await repository.add_idempotent(
                ticket("00000000-0000-0000-0000-000000000603"),
                "same-key",
                "different-fingerprint",
            )

        concurrent = await asyncio.gather(
            repository.add_idempotent(
                ticket("00000000-0000-0000-0000-000000000604"),
                "concurrent-key",
                "concurrent-fingerprint",
            ),
            repository.add_idempotent(
                ticket("00000000-0000-0000-0000-000000000605"),
                "concurrent-key",
                "concurrent-fingerprint",
            ),
        )
        assert sorted(result.created for result in concurrent) == [False, True]
        assert concurrent[0].ticket.id == concurrent[1].ticket.id
        assert len(await repository.list(TicketFilter())) == 2
        await engine.dispose()

    asyncio.run(exercise())
