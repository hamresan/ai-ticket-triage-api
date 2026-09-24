from dataclasses import dataclass

from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)


@dataclass(frozen=True, slots=True)
class FallbackRule:
    priority: Priority
    sentiment: Sentiment
    needs_human_review: bool
    reply: str


@dataclass(frozen=True, slots=True)
class FallbackDecisionCatalog:
    rules: dict[Category, FallbackRule]

    @classmethod
    def default(cls) -> "FallbackDecisionCatalog":
        return cls(
            rules={
                Category.REFUND: FallbackRule(
                    Priority.HIGH, Sentiment.NEGATIVE, False, "We received your refund request."
                ),
                Category.BILLING: FallbackRule(
                    Priority.MEDIUM, Sentiment.NEUTRAL, False, "We received your billing question."
                ),
                Category.ACCOUNT_ACCESS: FallbackRule(
                    Priority.HIGH,
                    Sentiment.NEGATIVE,
                    True,
                    "A specialist will review your account access request.",
                ),
                Category.TECHNICAL: FallbackRule(
                    Priority.MEDIUM, Sentiment.NEGATIVE, False, "We received your technical issue."
                ),
                Category.ABUSIVE: FallbackRule(
                    Priority.URGENT,
                    Sentiment.FRUSTRATED,
                    True,
                    "A support specialist will review your request.",
                ),
                Category.UNKNOWN: FallbackRule(
                    Priority.MEDIUM,
                    Sentiment.NEUTRAL,
                    True,
                    "A support specialist will review your request.",
                ),
            }
        )

    def build(self, category: Category) -> TriageDecision:
        rule = self.rules[category]
        return TriageDecision(
            category=category,
            priority=rule.priority,
            sentiment=rule.sentiment,
            needs_human_review=rule.needs_human_review,
            suggested_reply=SuggestedReply(rule.reply),
            provenance=TriageProvenance.FALLBACK,
        )
