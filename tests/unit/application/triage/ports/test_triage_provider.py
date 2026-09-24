from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.application.triage.ports import TriageProvider
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)
from tests.unit.application.support import ScriptedTriageProvider


@pytest.mark.asyncio
async def test_triage_provider_contract_can_be_exercised_without_infrastructure() -> None:
    decision = TriageDecision(
        category=Category.BILLING,
        priority=Priority.HIGH,
        sentiment=Sentiment.FRUSTRATED,
        needs_human_review=True,
        suggested_reply=SuggestedReply("An agent will review the duplicate charge."),
        provenance=TriageProvenance.PROVIDER,
    )
    provider: TriageProvider = ScriptedTriageProvider(decision)
    ticket = Ticket(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        subject=TicketSubject("Charged twice"),
        message=TicketMessage("Please review both charges."),
        status=TicketStatus.NEW,
        created_at=datetime(2026, 9, 24, tzinfo=UTC),
        updated_at=datetime(2026, 9, 24, tzinfo=UTC),
    )

    assert await provider.triage(ticket) == decision
