from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.errors import InvalidTicketStateError
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject
from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)

TICKET_ID = UUID("00000000-0000-0000-0000-000000000001")
NOW = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def build_decision() -> TriageDecision:
    return TriageDecision(
        category=Category.TECHNICAL,
        priority=Priority.MEDIUM,
        sentiment=Sentiment.NEGATIVE,
        needs_human_review=False,
        suggested_reply=SuggestedReply("We are reviewing the technical issue."),
        provenance=TriageProvenance.PROVIDER,
    )


def build_new_ticket() -> Ticket:
    return Ticket(
        id=TICKET_ID,
        subject=TicketSubject("Cannot sign in"),
        message=TicketMessage("The login page returns an error."),
        status=TicketStatus.NEW,
        created_at=NOW,
        updated_at=NOW,
    )


def test_new_ticket_has_no_decision() -> None:
    ticket = build_new_ticket()

    assert ticket.status is TicketStatus.NEW
    assert ticket.decision is None


def test_ticket_is_immutable() -> None:
    ticket = build_new_ticket()

    with pytest.raises(FrozenInstanceError):
        ticket.status = TicketStatus.FAILED  # type: ignore[misc]


def test_new_ticket_can_transition_to_triaged() -> None:
    decision = build_decision()
    updated_at = NOW + timedelta(seconds=1)

    ticket = build_new_ticket().mark_triaged(decision, updated_at=updated_at)

    assert ticket.status is TicketStatus.TRIAGED
    assert ticket.decision == decision
    assert ticket.updated_at == updated_at


def test_new_ticket_can_transition_to_failed_without_decision() -> None:
    ticket = build_new_ticket().mark_failed(updated_at=NOW + timedelta(seconds=1))

    assert ticket.status is TicketStatus.FAILED
    assert ticket.decision is None


@pytest.mark.parametrize("status", [TicketStatus.TRIAGED, TicketStatus.FAILED])
def test_terminal_statuses_cannot_transition(status: TicketStatus) -> None:
    decision = build_decision() if status is TicketStatus.TRIAGED else None
    ticket = Ticket(
        id=TICKET_ID,
        subject=TicketSubject("Cannot sign in"),
        message=TicketMessage("The login page returns an error."),
        status=status,
        created_at=NOW,
        updated_at=NOW,
        decision=decision,
    )

    with pytest.raises(InvalidTicketStateError):
        ticket.mark_failed(updated_at=NOW + timedelta(seconds=1))


def test_transition_time_cannot_move_backwards() -> None:
    with pytest.raises(InvalidTicketStateError):
        build_new_ticket().mark_failed(updated_at=NOW - timedelta(seconds=1))


def test_ticket_updated_at_cannot_precede_created_at() -> None:
    with pytest.raises(InvalidTicketStateError):
        Ticket(
            id=TICKET_ID,
            subject=TicketSubject("Cannot sign in"),
            message=TicketMessage("The login page returns an error."),
            status=TicketStatus.NEW,
            created_at=NOW,
            updated_at=NOW - timedelta(seconds=1),
        )


def test_triaged_ticket_requires_decision() -> None:
    with pytest.raises(InvalidTicketStateError):
        Ticket(
            id=TICKET_ID,
            subject=TicketSubject("Cannot sign in"),
            message=TicketMessage("The login page returns an error."),
            status=TicketStatus.TRIAGED,
            created_at=NOW,
            updated_at=NOW,
        )


@pytest.mark.parametrize("status", [TicketStatus.NEW, TicketStatus.FAILED])
def test_non_triaged_ticket_rejects_decision(status: TicketStatus) -> None:
    with pytest.raises(InvalidTicketStateError):
        Ticket(
            id=TICKET_ID,
            subject=TicketSubject("Cannot sign in"),
            message=TicketMessage("The login page returns an error."),
            status=status,
            created_at=NOW,
            updated_at=NOW,
            decision=build_decision(),
        )
