from enum import StrEnum


class TicketStatusQuery(StrEnum):
    NEW = "new"
    TRIAGED = "triaged"
    FAILED = "failed"
