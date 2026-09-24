from typing import Any, cast

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.structured.contracts import (
    TriageTaskOutputV1,
)

_REQUIRED_FIELDS = {
    "category",
    "priority",
    "sentiment",
    "needs_human_review",
    "suggested_reply",
}


class StructuredTriageOutputValidator:
    def validate(self, payload: Any) -> TriageTaskOutputV1:
        if not isinstance(payload, dict):
            raise TriageProviderError("Provider response does not match the v1 schema.")
        fields = cast(dict[str, object], payload)
        if set(fields) != _REQUIRED_FIELDS:
            raise TriageProviderError("Provider response does not match the v1 schema.")
        category = fields["category"]
        priority = fields["priority"]
        sentiment = fields["sentiment"]
        human_review = fields["needs_human_review"]
        suggested_reply = fields["suggested_reply"]
        if (
            not isinstance(category, str)
            or not isinstance(priority, str)
            or not isinstance(sentiment, str)
            or type(human_review) is not bool
            or not isinstance(suggested_reply, str)
        ):
            raise TriageProviderError("Provider response contains invalid field types.")
        return TriageTaskOutputV1(
            category=category,
            priority=priority,
            sentiment=sentiment,
            needs_human_review=human_review,
            suggested_reply=suggested_reply,
        )
