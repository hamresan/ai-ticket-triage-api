class TriageDomainError(ValueError):
    """Base error for invalid triage domain values."""


class EmptySuggestedReplyError(TriageDomainError):
    """Raised when a suggested reply is blank."""


class SuggestedReplyTooLongError(TriageDomainError):
    """Raised when a suggested reply exceeds its maximum length."""
