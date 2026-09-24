from dataclasses import FrozenInstanceError
from uuid import UUID

import pytest

from ai_ticket_triage.application.triage.dto import TriageTicketInput


def test_triage_ticket_input_is_immutable() -> None:
    ticket_id = UUID("00000000-0000-0000-0000-000000000005")
    dto = TriageTicketInput(ticket_id=ticket_id)

    assert dto.ticket_id == ticket_id
    with pytest.raises(FrozenInstanceError):
        dto.ticket_id = UUID(int=0)  # type: ignore[misc]
