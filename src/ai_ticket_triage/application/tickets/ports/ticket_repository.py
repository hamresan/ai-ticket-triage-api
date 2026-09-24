from typing import Protocol
from uuid import UUID

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.domain.tickets import Ticket


class TicketRepository(Protocol):
    async def add(self, ticket: Ticket) -> None: ...

    async def update(self, ticket: Ticket) -> None: ...

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None: ...

    async def list(self, filters: TicketFilter) -> tuple[Ticket, ...]: ...
