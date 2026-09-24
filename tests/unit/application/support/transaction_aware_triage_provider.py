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
from tests.unit.application.support.transaction_tracking_repository import (
    TransactionTrackingTicketRepository,
)


class TransactionAwareTriageProvider(TriageProvider):
    def __init__(self, repository: TransactionTrackingTicketRepository) -> None:
        self._repository = repository
        self.called_outside_write = False

    async def triage(self, ticket: Ticket) -> TriageDecision:
        self.called_outside_write = not self._repository.write_in_progress
        return TriageDecision(
            category=Category.TECHNICAL,
            priority=Priority.MEDIUM,
            sentiment=Sentiment.NEUTRAL,
            needs_human_review=False,
            suggested_reply=SuggestedReply("Transaction boundary draft."),
            provenance=TriageProvenance.PROVIDER,
        )
