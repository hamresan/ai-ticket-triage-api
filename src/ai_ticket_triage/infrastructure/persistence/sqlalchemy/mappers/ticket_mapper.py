from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models import TicketModel


class TicketMapper:
    @staticmethod
    def to_model(ticket: Ticket) -> TicketModel:
        return TicketModel(id=ticket.id, subject=ticket.subject.value, message=ticket.message.value, status=ticket.status.value, created_at=ticket.created_at, updated_at=ticket.updated_at)

    @staticmethod
    def to_domain(model: TicketModel) -> Ticket:
        return Ticket(id=model.id, subject=TicketSubject(model.subject), message=TicketMessage(model.message), status=TicketStatus(model.status), created_at=model.created_at, updated_at=model.updated_at)
