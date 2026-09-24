from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)
from ai_ticket_triage.domain.triage.errors import TriageDomainError
from ai_ticket_triage.infrastructure.providers.structured.parser import StructuredTriageOutputParser


class StructuredTriageResponseMapper:
    def __init__(self, parser: StructuredTriageOutputParser | None = None) -> None:
        self._parser = parser or StructuredTriageOutputParser()

    def map(self, content: str) -> TriageDecision:
        output = self._parser.parse(content)
        try:
            return TriageDecision(
                category=Category(output.category),
                priority=Priority(output.priority),
                sentiment=Sentiment(output.sentiment),
                needs_human_review=output.needs_human_review,
                suggested_reply=SuggestedReply(output.suggested_reply),
                provenance=TriageProvenance.PROVIDER,
            )
        except (ValueError, TriageDomainError) as exc:
            message = "Provider response contains an invalid triage value."
            raise TriageProviderError(message) from exc
