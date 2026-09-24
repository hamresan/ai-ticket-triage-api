from dataclasses import dataclass

from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)
from ai_ticket_triage.domain.triage.policies.signals import TriageSignalDetector


@dataclass(frozen=True, slots=True)
class DeterministicTriagePolicy:
    detector: TriageSignalDetector

    def decide(self, ticket: Ticket) -> TriageDecision:
        text = f"{ticket.subject.value} {ticket.message.value}"
        categories = self.detector.detect(text)
        if len(categories) != 1:
            return TriageDecision(
                category=Category.UNKNOWN,
                priority=Priority.MEDIUM,
                sentiment=Sentiment.NEUTRAL,
                needs_human_review=True,
                suggested_reply=SuggestedReply(
                    "Thanks for contacting support. A specialist will review your request."
                ),
                provenance=TriageProvenance.FALLBACK,
            )

        category = next(iter(categories))
        decisions = {
            Category.REFUND: (Priority.HIGH, Sentiment.NEGATIVE, False, "We received your refund request and will review it."),
            Category.BILLING: (Priority.MEDIUM, Sentiment.NEUTRAL, False, "We received your billing question and will review it."),
            Category.ACCOUNT_ACCESS: (Priority.HIGH, Sentiment.NEGATIVE, True, "We received your account access request. A specialist will review it."),
            Category.TECHNICAL: (Priority.MEDIUM, Sentiment.NEGATIVE, False, "We received your technical issue and will review it."),
            Category.ABUSIVE: (Priority.URGENT, Sentiment.FRUSTRATED, True, "A support specialist will review your request."),
        }
        priority, sentiment, human_review, reply = decisions[category]
        return TriageDecision(
            category=category,
            priority=priority,
            sentiment=sentiment,
            needs_human_review=human_review,
            suggested_reply=SuggestedReply(reply),
            provenance=TriageProvenance.FALLBACK,
        )
