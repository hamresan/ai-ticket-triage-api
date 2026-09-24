from dataclasses import dataclass

from ai_ticket_triage.domain.triage.errors import EmptySuggestedReplyError, SuggestedReplyTooLongError

MAX_SUGGESTED_REPLY_LENGTH = 4_000


@dataclass(frozen=True, slots=True)
class SuggestedReply:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise EmptySuggestedReplyError("Suggested reply must not be empty.")
        if len(self.value) > MAX_SUGGESTED_REPLY_LENGTH:
            raise SuggestedReplyTooLongError(
                f"Suggested reply must not exceed {MAX_SUGGESTED_REPLY_LENGTH} characters."
            )
