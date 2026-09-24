from dataclasses import dataclass

from ai_ticket_triage.domain.tickets import Ticket


@dataclass(frozen=True, slots=True)
class CreateTicketInput:
    subject: str
    message: str


@dataclass(frozen=True, slots=True)
class TicketOutput:
    ticket: Ticket
