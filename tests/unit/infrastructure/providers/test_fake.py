import asyncio
from datetime import UTC, datetime
from uuid import UUID

from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import Category, Priority, Sentiment, TriageProvenance
from ai_ticket_triage.infrastructure.providers import FakeTriageProvider


def test_fake_provider_returns_configured_provider_decision() -> None:
    async def exercise() -> None:
        now = datetime(2026, 9, 24, tzinfo=UTC)
        ticket = Ticket(
            id=UUID("00000000-0000-0000-0000-000000000304"),
            subject=TicketSubject("Question"),
            message=TicketMessage("Please help."),
            status=TicketStatus.NEW,
            created_at=now,
            updated_at=now,
        )
        provider = FakeTriageProvider(
            category=Category.REFUND,
            priority=Priority.HIGH,
            sentiment=Sentiment.NEGATIVE,
            needs_human_review=True,
            suggested_reply="Configured draft.",
        )

        decision = await provider.triage(ticket)

        assert decision.category is Category.REFUND
        assert decision.priority is Priority.HIGH
        assert decision.sentiment is Sentiment.NEGATIVE
        assert decision.needs_human_review is True
        assert decision.suggested_reply.value == "Configured draft."
        assert decision.provenance is TriageProvenance.PROVIDER

    asyncio.run(exercise())
