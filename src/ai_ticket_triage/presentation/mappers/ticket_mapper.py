from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.presentation.schemas import CreateTicketRequest, TicketResponse


class TicketPresentationMapper:
    @staticmethod
    def to_create_input(request: CreateTicketRequest) -> CreateTicketInput:
        return CreateTicketInput(subject=request.subject, message=request.message)

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
