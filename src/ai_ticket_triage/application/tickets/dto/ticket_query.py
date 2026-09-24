from dataclasses import dataclass

from ai_ticket_triage.domain.tickets import TicketStatus


@dataclass(frozen=True, slots=True)
class TicketFilter:
    status: TicketStatus | None = None
