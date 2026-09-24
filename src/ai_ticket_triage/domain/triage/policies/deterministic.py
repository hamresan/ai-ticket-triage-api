from dataclasses import dataclass

from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.domain.triage import Category, TriageDecision
from ai_ticket_triage.domain.triage.policies.fallback_catalog import FallbackDecisionCatalog
from ai_ticket_triage.domain.triage.policies.signals import TriageSignalDetector


@dataclass(frozen=True, slots=True)
class DeterministicTriagePolicy:
    detector: TriageSignalDetector
    catalog: FallbackDecisionCatalog

    def decide(self, ticket: Ticket) -> TriageDecision:
        text = f"{ticket.subject.value} {ticket.message.value}"
        categories = self.detector.detect(text)
        category = next(iter(categories)) if len(categories) == 1 else Category.UNKNOWN
        return self.catalog.build(category)
