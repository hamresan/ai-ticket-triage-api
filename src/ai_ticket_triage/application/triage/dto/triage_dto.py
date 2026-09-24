from dataclasses import dataclass
from uuid import UUID

from ai_ticket_triage.domain.tickets import Ticket


@dataclass(frozen=True, slots=True)
class TriageTicketInput:
    ticket_id: UUID


@dataclass(frozen=True, slots=True)
class TriageTicketOutput:
    ticket: Ticket
