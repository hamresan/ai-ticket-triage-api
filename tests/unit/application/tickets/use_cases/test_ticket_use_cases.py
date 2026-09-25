import asyncio
from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.errors import IdempotencyConflictError
from ai_ticket_triage.application.tickets.policies import TicketRequestFingerprint
from ai_ticket_triage.application.tickets.use_cases import CreateTicket, GetTicket, ListTickets
from ai_ticket_triage.domain.tickets import TicketStatus
from tests.unit.application.support import InMemoryTicketRepository

TICKET_ID = UUID("00000000-0000-0000-0000-000000000201")
NOW = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def test_ticket_use_cases_create_get_and_filter() -> None:
    repository = InMemoryTicketRepository()
    create_ticket = CreateTicket(
        repository, lambda: TICKET_ID, lambda: NOW, TicketRequestFingerprint()
    )
    get_ticket = GetTicket(repository)
    list_tickets = ListTickets(repository)

    async def exercise() -> None:
        created = await create_ticket.execute(
            CreateTicketInput(
                subject="Account access",
                message="I cannot sign in.",
                idempotency_key="request-201",
            )
        )
        assert created.created is True
        assert created.ticket.id == TICKET_ID
        assert created.ticket.status is TicketStatus.NEW
        assert await get_ticket.execute(TICKET_ID) == created.ticket
        assert await get_ticket.execute(UUID(int=0)) is None
        assert await list_tickets.execute(TicketFilter()) == (created.ticket,)
        assert await list_tickets.execute(TicketFilter(status=TicketStatus.NEW)) == (
            created.ticket,
        )
        assert await list_tickets.execute(TicketFilter(status=TicketStatus.FAILED)) == ()

    asyncio.run(exercise())


def test_create_ticket_replays_same_idempotent_request_without_duplicate() -> None:
    repository = InMemoryTicketRepository()
    ids = iter((TICKET_ID, UUID("00000000-0000-0000-0000-000000000202")))
    create_ticket = CreateTicket(
        repository, lambda: next(ids), lambda: NOW, TicketRequestFingerprint()
    )
    request = CreateTicketInput(
        subject="Account access",
        message="I cannot sign in.",
        idempotency_key="same-key",
    )

    async def exercise() -> None:
        first = await create_ticket.execute(request)
        second = await create_ticket.execute(request)

        assert first.created is True
        assert second.created is False
        assert second.ticket == first.ticket
        assert len(repository.tickets) == 1

    asyncio.run(exercise())


def test_create_ticket_rejects_key_reuse_with_different_payload() -> None:
    repository = InMemoryTicketRepository()
    ids = iter((TICKET_ID, UUID("00000000-0000-0000-0000-000000000203")))
    create_ticket = CreateTicket(
        repository, lambda: next(ids), lambda: NOW, TicketRequestFingerprint()
    )

    async def exercise() -> None:
        await create_ticket.execute(CreateTicketInput("Subject", "First body", "conflict-key"))
        with pytest.raises(IdempotencyConflictError):
            await create_ticket.execute(
                CreateTicketInput("Subject", "Different body", "conflict-key")
            )

    asyncio.run(exercise())
