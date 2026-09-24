from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import Category, Priority, Sentiment, TriageProvenance
from ai_ticket_triage.domain.triage.policies import (
    DeterministicTriagePolicy,
    FallbackDecisionCatalog,
    TriageSignalDetector,
)


def build_ticket(subject: str, message: str = "Please help.") -> Ticket:
    now = datetime(2026, 9, 24, tzinfo=UTC)
    return Ticket(
        id=UUID("00000000-0000-0000-0000-000000000301"),
        subject=TicketSubject(subject),
        message=TicketMessage(message),
        status=TicketStatus.NEW,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.parametrize(
    ("text", "category", "priority", "sentiment", "human_review"),
    [
        ("I need a refund", Category.REFUND, Priority.HIGH, Sentiment.NEGATIVE, False),
        ("Billing question", Category.BILLING, Priority.MEDIUM, Sentiment.NEUTRAL, False),
        ("I cannot log in", Category.ACCOUNT_ACCESS, Priority.HIGH, Sentiment.NEGATIVE, True),
        ("The app has an error", Category.TECHNICAL, Priority.MEDIUM, Sentiment.NEGATIVE, False),
        ("Your service is useless", Category.ABUSIVE, Priority.URGENT, Sentiment.FRUSTRATED, True),
    ],
)
def test_known_signal_boundaries(text, category, priority, sentiment, human_review) -> None:
    decision = DeterministicTriagePolicy(
        TriageSignalDetector.default(), FallbackDecisionCatalog.default()
    ).decide(build_ticket(text))

    assert decision.category is category
    assert decision.priority is priority
    assert decision.sentiment is sentiment
    assert decision.needs_human_review is human_review
    assert decision.provenance is TriageProvenance.FALLBACK


def test_unknown_input_requires_human_review() -> None:
    decision = DeterministicTriagePolicy(
        TriageSignalDetector.default(), FallbackDecisionCatalog.default()
    ).decide(build_ticket("General question"))

    assert decision.category is Category.UNKNOWN
    assert decision.needs_human_review is True


def test_conflicting_signals_require_human_review() -> None:
    decision = DeterministicTriagePolicy(
        TriageSignalDetector.default(), FallbackDecisionCatalog.default()
    ).decide(build_ticket("Refund", "I need a refund because I cannot log in."))

    assert decision.category is Category.UNKNOWN
    assert decision.needs_human_review is True
