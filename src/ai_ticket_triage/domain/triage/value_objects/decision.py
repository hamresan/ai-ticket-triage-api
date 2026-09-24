from dataclasses import dataclass

from ai_ticket_triage.domain.triage.value_objects.enums import (
    Category,
    Priority,
    Sentiment,
    TriageProvenance,
)
from ai_ticket_triage.domain.triage.value_objects.suggested_reply import SuggestedReply


@dataclass(frozen=True, slots=True)
class TriageDecision:
    category: Category
    priority: Priority
    sentiment: Sentiment
    needs_human_review: bool
    suggested_reply: SuggestedReply
    provenance: TriageProvenance
