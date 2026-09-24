from dataclasses import FrozenInstanceError

import pytest

from ai_ticket_triage.domain.triage import (
    Category,
    Priority,
    Sentiment,
    SuggestedReply,
    TriageDecision,
    TriageProvenance,
)
from ai_ticket_triage.domain.triage.errors import (
    EmptySuggestedReplyError,
    SuggestedReplyTooLongError,
)
from ai_ticket_triage.domain.triage.value_objects import MAX_SUGGESTED_REPLY_LENGTH


def test_triage_decision_is_immutable() -> None:
    decision = TriageDecision(
        category=Category.REFUND,
        priority=Priority.HIGH,
        sentiment=Sentiment.FRUSTRATED,
        needs_human_review=True,
        suggested_reply=SuggestedReply("I can help review your refund request."),
        provenance=TriageProvenance.PROVIDER,
    )

    with pytest.raises(FrozenInstanceError):
        decision.priority = Priority.LOW  # type: ignore[misc]


@pytest.mark.parametrize("value", ["", " ", "\n"])
def test_suggested_reply_rejects_blank_text(value: str) -> None:
    with pytest.raises(EmptySuggestedReplyError):
        SuggestedReply(value)


def test_suggested_reply_rejects_text_over_limit() -> None:
    with pytest.raises(SuggestedReplyTooLongError):
        SuggestedReply("x" * (MAX_SUGGESTED_REPLY_LENGTH + 1))


def test_suggested_reply_accepts_exact_limit() -> None:
    assert len(SuggestedReply("x" * MAX_SUGGESTED_REPLY_LENGTH).value) == MAX_SUGGESTED_REPLY_LENGTH
