from dataclasses import dataclass

from ai_ticket_triage.domain.tickets import TicketStatus
from ai_ticket_triage.domain.triage import Category, Priority


@dataclass(frozen=True, slots=True)
class TicketFilter:
    status: TicketStatus | None = None
    category: Category | None = None
    priority: Priority | None = None
    needs_human_review: bool | None = None
    offset: int = 0
    limit: int = 50
