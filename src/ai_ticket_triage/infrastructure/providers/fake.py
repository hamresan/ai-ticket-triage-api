from dataclasses import dataclass

from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)


@dataclass(frozen=True, slots=True)
class FakeTriageProvider(TriageProvider):
    category: Category = Category.TECHNICAL
    priority: Priority = Priority.MEDIUM
    sentiment: Sentiment = Sentiment.NEUTRAL
    needs_human_review: bool = False
    suggested_reply: str = "This is a draft response from the Fake triage provider."

    async def triage(self, ticket: Ticket) -> TriageDecision:
        return TriageDecision(
            category=self.category,
            priority=self.priority,
            sentiment=self.sentiment,
            needs_human_review=self.needs_human_review,
            suggested_reply=SuggestedReply(self.suggested_reply),
            provenance=TriageProvenance.PROVIDER,
        )
