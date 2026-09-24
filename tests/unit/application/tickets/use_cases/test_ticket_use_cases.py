import asyncio
from datetime import UTC, datetime
from uuid import UUID

from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.use_cases import CreateTicket, GetTicket, ListTickets
from ai_ticket_triage.domain.tickets import TicketStatus
from tests.unit.application.support import InMemoryTicketRepository

TICKET_ID = UUID("00000000-0000-0000-0000-000000000201")
NOW = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def test_ticket_use_cases_create_get_and_filter() -> None:
    repository = InMemoryTicketRepository()
    create_ticket = CreateTicket(repository, lambda: TICKET_ID, lambda: NOW)
    get_ticket = GetTicket(repository)
    list_tickets = ListTickets(repository)

    async def exercise() -> None:
        created = await create_ticket.execute(
            CreateTicketInput(subject="Account access", message="I cannot sign in.")
        )
        assert created.id == TICKET_ID
        assert created.status is TicketStatus.NEW
        assert await get_ticket.execute(TICKET_ID) == created
        assert await get_ticket.execute(UUID(int=0)) is None
        assert await list_tickets.execute(TicketFilter()) == (created,)
        assert await list_tickets.execute(TicketFilter(status=TicketStatus.NEW)) == (created,)
        assert await list_tickets.execute(TicketFilter(status=TicketStatus.FAILED)) == ()

    asyncio.run(exercise())
