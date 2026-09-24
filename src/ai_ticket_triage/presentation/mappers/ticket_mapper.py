from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.presentation.schemas import (
    CreateTicketRequest,
    TicketResponse,
    TicketStatusQuery,
)


class TicketPresentationMapper:
    @staticmethod
    def to_create_input(request: CreateTicketRequest) -> CreateTicketInput:
        return CreateTicketInput(subject=request.subject, message=request.message)

    @staticmethod
    def to_filter(status: TicketStatusQuery | None) -> TicketFilter:
        return TicketFilter(status=TicketStatus(status.value) if status is not None else None)

    @staticmethod
    def to_response(ticket: Ticket) -> TicketResponse:
        return TicketResponse(
            id=ticket.id,
            subject=ticket.subject.value,
            message=ticket.message.value,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )
