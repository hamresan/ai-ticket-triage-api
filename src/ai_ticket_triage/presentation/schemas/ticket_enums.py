from enum import StrEnum


class TicketStatusResponse(StrEnum):
    NEW = "new"
    TRIAGED = "triaged"
    FAILED = "failed"


class CategoryResponse(StrEnum):
    REFUND = "refund"
    BILLING = "billing"
    ACCOUNT_ACCESS = "account_access"
    TECHNICAL = "technical"
    ABUSIVE = "abusive"
    UNKNOWN = "unknown"


class PriorityResponse(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class SentimentResponse(StrEnum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    FRUSTRATED = "frustrated"


class ProvenanceResponse(StrEnum):
    PROVIDER = "provider"
    FALLBACK = "fallback"
