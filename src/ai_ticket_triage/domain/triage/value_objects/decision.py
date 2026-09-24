from dataclasses import dataclass

from ai_ticket_triage.domain.triage.value_objects.enums import (
    Category,
    Priority,
    Sentiment,
    TriageProvenance,
)

MAX_SUGGESTED_REPLY_LENGTH = 4_000


@dataclass(frozen=True, slots=True)
class TriageDecision:
    category: Category
    priority: Priority
    sentiment: Sentiment
    needs_human_review: bool
    suggested_reply: str
    provenance: TriageProvenance

    def __post_init__(self) -> None:
        if not self.suggested_reply.strip():
            raise ValueError("Suggested reply must not be empty.")
        if len(self.suggested_reply) > MAX_SUGGESTED_REPLY_LENGTH:
            raise ValueError(
                f"Suggested reply must not exceed {MAX_SUGGESTED_REPLY_LENGTH} characters."
            )
