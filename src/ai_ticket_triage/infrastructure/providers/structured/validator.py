from typing import Any

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
        if not isinstance(payload, dict) or set(payload) != _REQUIRED_FIELDS:
            raise TriageProviderError("Provider response does not match the v1 schema.")
        category = payload["category"]
        priority = payload["priority"]
        sentiment = payload["sentiment"]
        human_review = payload["needs_human_review"]
        suggested_reply = payload["suggested_reply"]
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
