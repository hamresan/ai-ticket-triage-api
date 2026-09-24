from enum import StrEnum


class Category(StrEnum):
    REFUND = "refund"
    BILLING = "billing"
    ACCOUNT_ACCESS = "account_access"
    TECHNICAL = "technical"
    ABUSIVE = "abusive"
    UNKNOWN = "unknown"


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Sentiment(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"


class TriageProvenance(StrEnum):
    PROVIDER = "provider"
    FALLBACK = "fallback"
