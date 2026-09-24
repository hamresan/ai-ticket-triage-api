from typing import Protocol
from uuid import UUID

from ai_ticket_triage.domain.tickets import Ticket


class TicketRepository(Protocol):
    async def add(self, ticket: Ticket) -> None: ...

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None: ...

    async def list_all(self) -> tuple[Ticket, ...]: ...
