from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import TriageDecision


class FailingTriageProvider(TriageProvider):
    async def triage(self, ticket: Ticket) -> TriageDecision:
        raise TriageProviderError("Scripted provider failure.")
