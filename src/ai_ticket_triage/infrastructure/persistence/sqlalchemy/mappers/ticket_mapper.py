from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.mappers.datetime_normalizer import (
    DatabaseDateTimeNormalizer,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.mappers.decision_mapper import DecisionMapper
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models import TicketModel


class TicketMapper:
    @staticmethod
    def to_model(ticket: Ticket) -> TicketModel:
        model = TicketModel(
            id=ticket.id,
            subject=ticket.subject.value,
            message=ticket.message.value,
            status=ticket.status.value,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )
        DecisionMapper.apply_to_model(model, ticket.decision)
        return model

    @staticmethod
    def to_domain(model: TicketModel) -> Ticket:
        return Ticket(
            id=model.id,
            subject=TicketSubject(model.subject),
            message=TicketMessage(model.message),
            status=TicketStatus(model.status),
            created_at=DatabaseDateTimeNormalizer.as_utc(model.created_at),
            updated_at=DatabaseDateTimeNormalizer.as_utc(model.updated_at),
            decision=DecisionMapper.to_domain(model),
        )
