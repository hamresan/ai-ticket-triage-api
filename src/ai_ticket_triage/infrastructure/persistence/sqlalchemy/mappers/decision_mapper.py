from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models import TicketModel


class DecisionMapper:
    @staticmethod
    def apply_to_model(model: TicketModel, decision: TriageDecision | None) -> None:
        if decision is None:
            return
        model.category = decision.category.value
        model.priority = decision.priority.value
        model.sentiment = decision.sentiment.value
        model.needs_human_review = decision.needs_human_review
        model.suggested_reply = decision.suggested_reply.value
        model.provenance = decision.provenance.value

    @staticmethod
    def to_domain(model: TicketModel) -> TriageDecision | None:
        if model.category is None:
            return None
        if (
            model.priority is None
            or model.sentiment is None
            or model.needs_human_review is None
            or model.suggested_reply is None
            or model.provenance is None
        ):
            raise ValueError("Persisted triage decision is incomplete.")
        return TriageDecision(
            category=Category(model.category),
            priority=Priority(model.priority),
            sentiment=Sentiment(model.sentiment),
            needs_human_review=model.needs_human_review,
            suggested_reply=SuggestedReply(model.suggested_reply),
            provenance=TriageProvenance(model.provenance),
        )
