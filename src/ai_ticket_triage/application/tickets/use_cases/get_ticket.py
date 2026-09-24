from uuid import UUID

from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket


class GetTicket:
    def __init__(self, repository: TicketRepository) -> None:
        self._repository = repository

    async def execute(self, ticket_id: UUID) -> Ticket | None:
        return await self._repository.get_by_id(ticket_id)
