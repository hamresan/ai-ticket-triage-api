from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.triage import Category, Priority, TriageDecision
from ai_ticket_triage.presentation.schemas import (
    CategoryQuery,
    CategoryResponse,
    CreateTicketRequest,
    PriorityQuery,
    PriorityResponse,
    ProvenanceResponse,
    SentimentResponse,
    TicketResponse,
    TicketStatusQuery,
    TicketStatusResponse,
    TriageDecisionResponse,
)


class TicketPresentationMapper:
    @staticmethod
    def to_create_input(
        request: CreateTicketRequest, idempotency_key: str
    ) -> CreateTicketInput:
        return CreateTicketInput(
            subject=request.subject,
            message=request.message,
            idempotency_key=idempotency_key,
        )

    @staticmethod
    def to_filter(
        status: TicketStatusQuery | None,
        category: CategoryQuery | None,
        priority: PriorityQuery | None,
        needs_human_review: bool | None,
        offset: int,
        limit: int,
    ) -> TicketFilter:
        return TicketFilter(
            status=TicketStatus(status.value) if status is not None else None,
            category=Category(category.value) if category is not None else None,
            priority=Priority(priority.value) if priority is not None else None,
            needs_human_review=needs_human_review,
            offset=offset,
            limit=limit,
        )

    @staticmethod
    def to_decision_response(decision: TriageDecision | None) -> TriageDecisionResponse | None:
        if decision is None:
            return None
        return TriageDecisionResponse(
            category=CategoryResponse(decision.category.value),
            priority=PriorityResponse(decision.priority.value),
            sentiment=SentimentResponse(decision.sentiment.value),
            needs_human_review=decision.needs_human_review,
            suggested_reply=decision.suggested_reply.value,
            provenance=ProvenanceResponse(decision.provenance.value),
        )

    @staticmethod
    def to_response(ticket: Ticket) -> TicketResponse:
        return TicketResponse(
            id=ticket.id,
            subject=ticket.subject.value,
            message=ticket.message.value,
            status=TicketStatusResponse(ticket.status.value),
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            decision=TicketPresentationMapper.to_decision_response(ticket.decision),
        )
