from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import TriageDecision


class ScriptedTriageProvider(TriageProvider):
    def __init__(self, decision: TriageDecision) -> None:
        self.decision = decision

    async def triage(self, ticket: Ticket) -> TriageDecision:
        return self.decision
