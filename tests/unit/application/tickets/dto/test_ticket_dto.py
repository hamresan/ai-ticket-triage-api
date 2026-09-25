from dataclasses import FrozenInstanceError

import pytest

from ai_ticket_triage.application.tickets.dto import CreateTicketInput


def test_create_ticket_input_is_framework_free_and_immutable() -> None:
    dto = CreateTicketInput(\n        subject="Refund", message="Please refund this order.", idempotency_key="request-key"\n    )

    assert dto.subject == "Refund"
    assert dto.message == "Please refund this order."\n    assert dto.idempotency_key == "request-key"
    with pytest.raises(FrozenInstanceError):
        dto.subject = "Changed"  # type: ignore[misc]
