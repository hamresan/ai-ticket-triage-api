import json
from typing import Any

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.structured.contracts import TriageTaskOutputV1


MAX_PROVIDER_RESPONSE_LENGTH = 16_000
_REQUIRED_FIELDS = {
    "category",
    "priority",
    "sentiment",
    "needs_human_review",
    "suggested_reply",
}


class StructuredTriageOutputParser:
    def parse(self, content: str) -> TriageTaskOutputV1:
        if len(content) > MAX_PROVIDER_RESPONSE_LENGTH:
            raise TriageProviderError("Provider response exceeded the maximum allowed length.")
        try:
            payload: Any = json.loads(content)
        except json.JSONDecodeError as exc:
            raise TriageProviderError("Provider returned malformed JSON.") from exc
        if not isinstance(payload, dict) or set(payload) != _REQUIRED_FIELDS:
            raise TriageProviderError("Provider response does not match the v1 schema.")
        return self._validated_output(payload)

    @staticmethod
    def _validated_output(payload: dict[str, Any]) -> TriageTaskOutputV1:
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
