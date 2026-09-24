class TicketDomainError(ValueError):
    """Base error for invalid ticket domain state."""


class EmptyTicketTextError(TicketDomainError):
    """Raised when a required ticket text field is blank."""


class TicketTextTooLongError(TicketDomainError):
    """Raised when a bounded ticket text field exceeds its maximum length."""


class InvalidTicketStateError(TicketDomainError):
    """Raised when ticket state and transition invariants are violated."""
