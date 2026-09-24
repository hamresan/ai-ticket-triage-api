from dataclasses import dataclass

from ai_ticket_triage.domain.tickets.errors import EmptyTicketTextError, TicketTextTooLongError

MAX_SUBJECT_LENGTH = 200
MAX_MESSAGE_LENGTH = 10_000


@dataclass(frozen=True, slots=True)
class TicketSubject:
    value: str

    def __post_init__(self) -> None:
        _validate_bounded_text("subject", self.value, MAX_SUBJECT_LENGTH)


@dataclass(frozen=True, slots=True)
class TicketMessage:
    value: str

    def __post_init__(self) -> None:
        _validate_bounded_text("message", self.value, MAX_MESSAGE_LENGTH)


def _validate_bounded_text(field_name: str, value: str, max_length: int) -> None:
    if not value.strip():
        raise EmptyTicketTextError(f"Ticket {field_name} must not be empty.")
    if len(value) > max_length:
        raise TicketTextTooLongError(
            f"Ticket {field_name} must not exceed {max_length} characters."
        )
