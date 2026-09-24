from datetime import UTC, datetime
from uuid import UUID

import pytest

from ai_ticket_triage.infrastructure.persistence.sqlalchemy.mappers import DecisionMapper
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models import TicketModel


def test_incomplete_persisted_decision_is_rejected() -> None:
    now = datetime(2026, 9, 24, tzinfo=UTC)
    model = TicketModel(
        id=UUID("00000000-0000-0000-0000-000000000307"),
        subject="Technical",
        message="Not working.",
        status="triaged",
        created_at=now,
        updated_at=now,
        category="technical",
    )

    with pytest.raises(ValueError, match="incomplete"):
        DecisionMapper.to_domain(model)
