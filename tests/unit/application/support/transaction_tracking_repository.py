from uuid import UUID

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket


class TransactionTrackingTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self.tickets: dict[UUID, Ticket] = {}
        self.write_in_progress = False

    async def add(self, ticket: Ticket) -> None:
        self.write_in_progress = True
        self.tickets[ticket.id] = ticket
        self.write_in_progress = False

    async def update(self, ticket: Ticket) -> None:
        self.write_in_progress = True
        self.tickets[ticket.id] = ticket
        self.write_in_progress = False

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.tickets.get(ticket_id)

    async def list(self, filters: TicketFilter) -> tuple[Ticket, ...]:
        return tuple(self.tickets.values())
