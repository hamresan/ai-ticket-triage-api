from enum import StrEnum


class TicketStatus(StrEnum):
    NEW = "new"
    TRIAGED = "triaged"
    FAILED = "failed"
