import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import IntegrityError

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
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
