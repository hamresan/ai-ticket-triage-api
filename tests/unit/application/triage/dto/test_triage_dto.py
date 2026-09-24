from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.application.triage.dto import TriageTicketInput, TriageTicketOutput
from ai_ticket_triage.domain.tickets import Ticket, TicketStatus
from ai_ticket_triage.domain.tickets.value_objects import TicketMessage, TicketSubject


def test_triage_ticket_input_is_immutable() -> None:
    ticket_id = UUID("00000000-0000-0000-0000-000000000005")
    dto = TriageTicketInput(ticket_id=ticket_id)

    assert dto.ticket_id == ticket_id
    with pytest.raises(FrozenInstanceError):
        dto.ticket_id = UUID(int=0)  # type: ignore[misc]


def test_triage_ticket_output_wraps_domain_ticket() -> None:
    now = datetime(2026, 9, 24, tzinfo=UTC)
    ticket = Ticket(
        id=UUID("00000000-0000-0000-0000-000000000005"),
        subject=TicketSubject("Technical issue"),
        message=TicketMessage("The application is unavailable."),
        status=TicketStatus.NEW,
        created_at=now,
        updated_at=now,
    )

    assert TriageTicketOutput(ticket=ticket).ticket == ticket
