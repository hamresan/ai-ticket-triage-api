import pytest

from ai_ticket_triage.domain.tickets import TicketStatus
from ai_ticket_triage.domain.triage import Category, Priority, Sentiment, TriageProvenance


@pytest.mark.parametrize(
    ("enum_type", "invalid_value"),
    [
        (TicketStatus, "pending"),
        (Category, "sales"),
        (Priority, "critical"),
        (Sentiment, "furious"),
        (TriageProvenance, "manual"),
    ],
)
def test_domain_enums_reject_unsupported_values(enum_type: type, invalid_value: str) -> None:
    with pytest.raises(ValueError):
        enum_type(invalid_value)


def test_status_values_are_exactly_the_supported_workflow_states() -> None:
    assert {status.value for status in TicketStatus} == {"new", "triaged", "failed"}
