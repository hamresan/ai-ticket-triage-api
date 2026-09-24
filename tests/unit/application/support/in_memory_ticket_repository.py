from uuid import UUID

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self.tickets: dict[UUID, Ticket] = {}

    async def add(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.tickets.get(ticket_id)

    async def list(self, filters: TicketFilter) -> tuple[Ticket, ...]:
        return tuple(
            ticket
            for ticket in self.tickets.values()
            if filters.status is None or ticket.status is filters.status
        )
