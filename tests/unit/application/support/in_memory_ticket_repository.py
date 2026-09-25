from uuid import UUID

from ai_ticket_triage.application.tickets.dto import TicketCreationResult
from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.errors import IdempotencyConflictError
from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket


class InMemoryTicketRepository(TicketRepository):
    def __init__(self) -> None:
        self.tickets: dict[UUID, Ticket] = {}
        self.idempotency: dict[str, tuple[str, UUID]] = {}

    async def add(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    async def add_idempotent(
        self, ticket: Ticket, idempotency_key: str, fingerprint: str
    ) -> TicketCreationResult:
        existing = self.idempotency.get(idempotency_key)
        if existing is not None:
            existing_fingerprint, ticket_id = existing
            if existing_fingerprint != fingerprint:
                raise IdempotencyConflictError
            return TicketCreationResult(ticket=self.tickets[ticket_id], created=False)
        self.tickets[ticket.id] = ticket
        self.idempotency[idempotency_key] = (fingerprint, ticket.id)
        return TicketCreationResult(ticket=ticket, created=True)

    async def update(self, ticket: Ticket) -> None:
        self.tickets[ticket.id] = ticket

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        return self.tickets.get(ticket_id)

    async def list(self, filters: TicketFilter) -> tuple[Ticket, ...]:
        tickets = sorted(self.tickets.values(), key=lambda ticket: (ticket.created_at, ticket.id))
        filtered = [
            ticket
            for ticket in tickets
            if (filters.status is None or ticket.status is filters.status)
            and (
                filters.category is None
                or (ticket.decision is not None and ticket.decision.category is filters.category)
            )
            and (
                filters.priority is None
                or (ticket.decision is not None and ticket.decision.priority is filters.priority)
            )
            and (
                filters.needs_human_review is None
                or (
                    ticket.decision is not None
                    and ticket.decision.needs_human_review is filters.needs_human_review
                )
            )
        ]
        return tuple(filtered[filters.offset : filters.offset + filters.limit])
