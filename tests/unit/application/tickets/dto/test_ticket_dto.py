from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.application.tickets.dto import CreateTicketInput, TicketOutput
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject


def test_create_ticket_input_is_framework_free_and_immutable() -> None:
    dto = CreateTicketInput(subject="Refund", message="Please refund this order.")

    assert dto.subject == "Refund"
    assert dto.message == "Please refund this order."
    with pytest.raises(FrozenInstanceError):
        dto.subject = "Changed"  # type: ignore[misc]


def test_ticket_output_wraps_domain_ticket() -> None:
    now = datetime(2026, 9, 24, tzinfo=UTC)
    ticket = Ticket(
        id=UUID("00000000-0000-0000-0000-000000000004"),
        subject=TicketSubject("Refund"),
        message=TicketMessage("Please refund this order."),
        status=TicketStatus.NEW,
        created_at=now,
        updated_at=now,
    )

    assert TicketOutput(ticket=ticket).ticket == ticket
