from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from ai_ticket_triage.domain.tickets.errors import InvalidTicketStateError
from ai_ticket_triage.domain.tickets.policies import TicketTransitionPolicy
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketStatus, TicketSubject
from ai_ticket_triage.domain.triage import TriageDecision


@dataclass(frozen=True, slots=True)
class Ticket:
    id: UUID
    subject: TicketSubject
    message: TicketMessage
    status: TicketStatus
    created_at: datetime
    updated_at: datetime
    decision: TriageDecision | None = None

    def __post_init__(self) -> None:
        if self.updated_at < self.created_at:
            raise InvalidTicketStateError("Ticket updated_at cannot be before created_at.")
        if self.status is TicketStatus.TRIAGED and self.decision is None:
            raise InvalidTicketStateError("A triaged ticket must have a triage decision.")
        if self.status is not TicketStatus.TRIAGED and self.decision is not None:
            raise InvalidTicketStateError("Only a triaged ticket may have a triage decision.")

    def mark_triaged(self, decision: TriageDecision, *, updated_at: datetime) -> "Ticket":
        TicketTransitionPolicy.validate(self.status, self.updated_at, updated_at)
        return replace(
            self,
            status=TicketStatus.TRIAGED,
            decision=decision,
            updated_at=updated_at,
        )

    def mark_failed(self, *, updated_at: datetime) -> "Ticket":
        TicketTransitionPolicy.validate(self.status, self.updated_at, updated_at)
        return replace(self, status=TicketStatus.FAILED, updated_at=updated_at)
