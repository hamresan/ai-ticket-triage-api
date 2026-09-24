import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID

from ai_ticket_triage.application.tickets.dto import CreateTicketInput
from ai_ticket_triage.application.tickets.use_cases import CreateTicket
from ai_ticket_triage.application.triage.dto import TriageTicketInput
from ai_ticket_triage.application.triage.use_cases import TriageTicket
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
from ai_ticket_triage.domain.triage.policies import (
    DeterministicTriagePolicy,
    FallbackDecisionCatalog,
    TriageSignalDetector,
)
from tests.unit.application.support.failing_triage_provider import FailingTriageProvider
from tests.unit.application.support.in_memory_ticket_repository import InMemoryTicketRepository
from tests.unit.application.support.scripted_triage_provider import ScriptedTriageProvider
from tests.unit.application.support.transaction_aware_triage_provider import (
    TransactionAwareTriageProvider,
)
from tests.unit.application.support.transaction_tracking_repository import (
    TransactionTrackingTicketRepository,
)


def build_ticket() -> Ticket:
    now = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
    return Ticket(
        id=UUID("00000000-0000-0000-0000-000000000302"),
        subject=TicketSubject("Refund request"),
        message=TicketMessage("I need a refund."),
        status=TicketStatus.NEW,
        created_at=now,
        updated_at=now,
    )


def test_provider_decision_is_persisted_with_provider_provenance() -> None:
    async def exercise() -> None:
        repository = InMemoryTicketRepository()
        ticket = build_ticket()
        await repository.add(ticket)
        decision = TriageDecision(
            category=Category.BILLING,
            priority=Priority.MEDIUM,
            sentiment=Sentiment.NEUTRAL,
            needs_human_review=False,
            suggested_reply=SuggestedReply("Billing draft."),
            provenance=TriageProvenance.PROVIDER,
        )
        use_case = TriageTicket(
            repository,
            ScriptedTriageProvider(decision),
            DeterministicTriagePolicy(
            TriageSignalDetector.default(), FallbackDecisionCatalog.default()
        ),
            lambda: ticket.updated_at + timedelta(seconds=1),
        )

        result = await use_case.execute(TriageTicketInput(ticket.id))

        assert result.status is TicketStatus.TRIAGED
        assert result.decision == decision
        assert await repository.get_by_id(ticket.id) == result

    asyncio.run(exercise())


def test_provider_failure_uses_fallback_and_remains_triaged() -> None:
    async def exercise() -> None:
        repository = InMemoryTicketRepository()
        ticket = build_ticket()
        await repository.add(ticket)
        use_case = TriageTicket(
            repository,
            FailingTriageProvider(),
            DeterministicTriagePolicy(
            TriageSignalDetector.default(), FallbackDecisionCatalog.default()
        ),
            lambda: ticket.updated_at + timedelta(seconds=1),
        )

        result = await use_case.execute(TriageTicketInput(ticket.id))

        assert result.status is TicketStatus.TRIAGED
        assert result.decision is not None
        assert result.decision.category is Category.REFUND
        assert result.decision.provenance is TriageProvenance.FALLBACK

    asyncio.run(exercise())


def test_provider_runs_after_create_write_boundary_is_closed() -> None:
    async def exercise() -> None:
        repository = TransactionTrackingTicketRepository()
        created_at = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
        ticket_id = UUID("00000000-0000-0000-0000-000000000305")
        create = CreateTicket(repository, lambda: ticket_id, lambda: created_at)
        provider = TransactionAwareTriageProvider(repository)
        triage = TriageTicket(
            repository,
            provider,
            DeterministicTriagePolicy(
            TriageSignalDetector.default(), FallbackDecisionCatalog.default()
        ),
            lambda: created_at + timedelta(seconds=1),
        )

        ticket = await create.execute(CreateTicketInput(subject="Error", message="Not working."))
        await triage.execute(TriageTicketInput(ticket.id))

        assert provider.called_outside_write is True
        assert repository.write_in_progress is False

    asyncio.run(exercise())
