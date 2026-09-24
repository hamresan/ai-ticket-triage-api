from dataclasses import dataclass

from ai_ticket_triage.application.tickets.use_cases import CreateTicket, GetTicket, ListTickets
from ai_ticket_triage.application.triage.use_cases import TriageTicket


@dataclass(frozen=True, slots=True)
class TicketUseCases:
    create: CreateTicket
    triage: TriageTicket
    get: GetTicket
    list: ListTickets
