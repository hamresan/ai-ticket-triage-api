from datetime import UTC, datetime


class DatabaseDateTimeNormalizer:
    @staticmethod
    def as_utc(value: datetime) -> datetime:
        return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
