from dataclasses import dataclass

from ai_ticket_triage.application.tickets.use_cases import CreateTicket, GetTicket, ListTickets


@dataclass(frozen=True, slots=True)
class TicketUseCases:
    create: CreateTicket
    get: GetTicket
    list: ListTickets
