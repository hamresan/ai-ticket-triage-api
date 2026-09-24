from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket


class ListTickets:
    def __init__(self, repository: TicketRepository) -> None:
        self._repository = repository

    async def execute(self, filters: TicketFilter) -> tuple[Ticket, ...]:
        return await self._repository.list(filters)
