from ai_ticket_triage.application.tickets.dto import TicketCreationResult
from ai_ticket_triage.domain.tickets import Ticket
from tests.unit.application.support.in_memory_ticket_repository import InMemoryTicketRepository


class TransactionTrackingTicketRepository(InMemoryTicketRepository):
    def __init__(self) -> None:
        super().__init__()
        self.write_in_progress = False

    async def add(self, ticket: Ticket) -> None:
        self.write_in_progress = True
        await super().add(ticket)
        self.write_in_progress = False

    async def add_idempotent(
        self, ticket: Ticket, idempotency_key: str, fingerprint: str
    ) -> TicketCreationResult:
        self.write_in_progress = True
        result = await super().add_idempotent(ticket, idempotency_key, fingerprint)
        self.write_in_progress = False
        return result

    async def update(self, ticket: Ticket) -> None:
        self.write_in_progress = True
        await super().update(ticket)
        self.write_in_progress = False
