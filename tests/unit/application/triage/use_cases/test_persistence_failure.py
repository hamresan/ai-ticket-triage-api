import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from ai_ticket_triage.application.triage.dto import TriageTicketInput
from ai_ticket_triage.application.triage.use_cases import TriageTicket
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage.policies import (
    DeterministicTriagePolicy,
    FallbackDecisionCatalog,
    TriageSignalDetector,
)
from tests.unit.application.support.failing_triage_provider import FailingTriageProvider
from tests.unit.application.support.failing_update_ticket_repository import (
    FailingUpdateTicketRepository,
)


def test_final_update_failure_preserves_persisted_new_state() -> None:
    async def exercise() -> None:
        now = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
        ticket = Ticket(
            id=UUID("00000000-0000-0000-0000-000000000308"),
            subject=TicketSubject("Refund request"),
            message=TicketMessage("I need a refund."),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        repository = FailingUpdateTicketRepository()
        await repository.add(ticket)
        use_case = TriageTicket(
            repository=repository,
            provider=FailingTriageProvider(),
            fallback=DeterministicTriagePolicy(
                TriageSignalDetector.default(),
                FallbackDecisionCatalog.default(),
            ),
            clock=lambda: now + timedelta(seconds=1),
        )

        with pytest.raises(RuntimeError, match="persistence failure"):
            await use_case.execute(TriageTicketInput(ticket.id))

        persisted = await repository.get_by_id(ticket.id)
        assert persisted == ticket
        assert persisted is not None
        assert persisted.status is TicketStatus.NEW
        assert persisted.decision is None

    asyncio.run(exercise())
