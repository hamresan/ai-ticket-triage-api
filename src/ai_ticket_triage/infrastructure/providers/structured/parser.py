import json
from typing import Any

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.infrastructure.providers.structured.contracts import TriageTaskOutputV1
from ai_ticket_triage.infrastructure.providers.structured.validator import (
    StructuredTriageOutputValidator,
)


MAX_PROVIDER_RESPONSE_LENGTH = 16_000


class StructuredTriageOutputParser:
    def __init__(self, validator: StructuredTriageOutputValidator | None = None) -> None:
        self._validator = validator or StructuredTriageOutputValidator()

    def parse(self, content: str) -> TriageTaskOutputV1:
        if len(content) > MAX_PROVIDER_RESPONSE_LENGTH:
            raise TriageProviderError("Provider response exceeded the maximum allowed length.")
        try:
            payload: Any = json.loads(content)
        except json.JSONDecodeError as exc:
            raise TriageProviderError("Provider returned malformed JSON.") from exc
        return self._validator.validate(payload)
