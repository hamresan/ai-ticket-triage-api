import pytest

from ai_ticket_triage.domain.tickets.errors import EmptyTicketTextError, TicketTextTooLongError
from ai_ticket_triage.domain.tickets.value_objects import (
    MAX_MESSAGE_LENGTH,
    MAX_SUBJECT_LENGTH,
    TicketMessage,
    TicketSubject,
)


def test_ticket_subject_accepts_bounded_text() -> None:
    subject = TicketSubject("Refund request")

    assert subject.value == "Refund request"


@pytest.mark.parametrize("value", ["", " ", "\n\t"])
def test_ticket_subject_rejects_blank_text(value: str) -> None:
    with pytest.raises(EmptyTicketTextError):
        TicketSubject(value)


def test_ticket_subject_rejects_text_over_limit() -> None:
    with pytest.raises(TicketTextTooLongError):
        TicketSubject("x" * (MAX_SUBJECT_LENGTH + 1))


def test_ticket_subject_accepts_exact_limit() -> None:
    assert len(TicketSubject("x" * MAX_SUBJECT_LENGTH).value) == MAX_SUBJECT_LENGTH


@pytest.mark.parametrize("value", ["", " ", "\n\t"])
def test_ticket_message_rejects_blank_text(value: str) -> None:
    with pytest.raises(EmptyTicketTextError):
        TicketMessage(value)


def test_ticket_message_rejects_text_over_limit() -> None:
    with pytest.raises(TicketTextTooLongError):
        TicketMessage("x" * (MAX_MESSAGE_LENGTH + 1))


def test_ticket_message_accepts_exact_limit() -> None:
    assert len(TicketMessage("x" * MAX_MESSAGE_LENGTH).value) == MAX_MESSAGE_LENGTH
