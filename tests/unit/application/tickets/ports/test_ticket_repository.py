from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from tests.unit.application.support import InMemoryTicketRepository


@pytest.mark.asyncio
async def test_ticket_repository_contract_can_be_exercised_without_infrastructure() -> None:
    repository: TicketRepository = InMemoryTicketRepository()
    ticket = Ticket(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        subject=TicketSubject("Billing question"),
        message=TicketMessage("I was charged twice."),
        status=TicketStatus.NEW,
        created_at=datetime(2026, 9, 24, tzinfo=UTC),
        updated_at=datetime(2026, 9, 24, tzinfo=UTC),
    )

    await repository.add(ticket)

    assert await repository.get_by_id(ticket.id) == ticket
    assert await repository.list_all() == (ticket,)
