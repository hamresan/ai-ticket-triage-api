from dataclasses import dataclass

from ai_ticket_triage.domain.tickets.policies.text_validation import TicketTextValidationPolicy

MAX_SUBJECT_LENGTH = 200
MAX_MESSAGE_LENGTH = 10_000


@dataclass(frozen=True, slots=True)
class TicketSubject:
    value: str

    def __post_init__(self) -> None:
        TicketTextValidationPolicy.validate("subject", self.value, MAX_SUBJECT_LENGTH)


@dataclass(frozen=True, slots=True)
class TicketMessage:
    value: str

    def __post_init__(self) -> None:
        TicketTextValidationPolicy.validate("message", self.value, MAX_MESSAGE_LENGTH)
