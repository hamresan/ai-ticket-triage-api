from typing import Protocol

from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import TriageDecision


class TriageProvider(Protocol):
    async def triage(self, ticket: Ticket) -> TriageDecision: ...
