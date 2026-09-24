from dataclasses import FrozenInstanceError

import pytest

from ai_ticket_triage.application.tickets.dto import CreateTicketInput


def test_create_ticket_input_is_framework_free_and_immutable() -> None:
    dto = CreateTicketInput(subject="Refund", message="Please refund this order.")

    assert dto.subject == "Refund"
    assert dto.message == "Please refund this order."
    with pytest.raises(FrozenInstanceError):
        dto.subject = "Changed"  # type: ignore[misc]
