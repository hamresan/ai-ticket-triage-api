from ai_ticket_triage.domain.tickets import Ticket
from tests.unit.application.support.in_memory_ticket_repository import InMemoryTicketRepository


class FailingUpdateTicketRepository(InMemoryTicketRepository):
    async def update(self, ticket: Ticket) -> None:
        raise RuntimeError("Scripted persistence failure.")
