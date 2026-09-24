from datetime import UTC, datetime, timedelta, timezone

from ai_ticket_triage.infrastructure.persistence.sqlalchemy.mappers.datetime_normalizer import (
    DatabaseDateTimeNormalizer,
)


def test_database_datetime_normalizer_adds_utc_to_naive_value() -> None:
    value = datetime(2026, 9, 24, 12, 0)

    assert DatabaseDateTimeNormalizer.as_utc(value) == datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def test_database_datetime_normalizer_converts_aware_value_to_utc() -> None:
    value = datetime(2026, 9, 24, 14, 0, tzinfo=timezone(timedelta(hours=2)))

    assert DatabaseDateTimeNormalizer.as_utc(value) == datetime(2026, 9, 24, 12, 0, tzinfo=UTC)
