from uuid import UUID

from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import TriageDecision


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self.tickets: dict[UUID, Ticket] = {}

    async def add(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.tickets.get(ticket_id)

    async def list_all(self) -> tuple[Ticket, ...]:
        return tuple(self.tickets.values())


class ScriptedTriageProvider(TriageProvider):
    def __init__(self, decision: TriageDecision) -> None:
        self.decision = decision

    async def triage(self, ticket: Ticket) -> TriageDecision:
        return self.decision
