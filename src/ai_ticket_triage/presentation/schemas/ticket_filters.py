from enum import StrEnum


class TicketStatusQuery(StrEnum):
    NEW = "new"
    TRIAGED = "triaged"
    FAILED = "failed"


class CategoryQuery(StrEnum):
    REFUND = "refund"
    BILLING = "billing"
    ACCOUNT_ACCESS = "account_access"
    TECHNICAL = "technical"
    ABUSIVE = "abusive"
    UNKNOWN = "unknown"


class PriorityQuery(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
