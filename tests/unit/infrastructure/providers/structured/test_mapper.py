import json

import pytest

from ai_ticket_triage.application.triage.errors import TriageProviderError
from ai_ticket_triage.domain.triage import Category, Priority, Sentiment, TriageProvenance
from ai_ticket_triage.infrastructure.providers.structured.mapper import (
    StructuredTriageResponseMapper,
)
from ai_ticket_triage.infrastructure.providers.structured.parser import (
    MAX_PROVIDER_RESPONSE_LENGTH,
    StructuredTriageOutputParser,
)
from ai_ticket_triage.infrastructure.providers.structured.validator import (
    StructuredTriageOutputValidator,
)


def build_mapper() -> StructuredTriageResponseMapper:
    return StructuredTriageResponseMapper(
        StructuredTriageOutputParser(StructuredTriageOutputValidator())
    )


def valid_payload() -> dict[str, object]:
    return {
        "category": "refund",
        "priority": "high",
        "sentiment": "negative",
        "needs_human_review": False,
        "suggested_reply": "We received your refund request.",
    }


def test_valid_structured_response_maps_to_domain_decision() -> None:
    decision = build_mapper().map(json.dumps(valid_payload()))

    assert decision.category is Category.REFUND
    assert decision.priority is Priority.HIGH
    assert decision.sentiment is Sentiment.NEGATIVE
    assert decision.provenance is TriageProvenance.PROVIDER


@pytest.mark.parametrize(
    "content",
    [
        "{not-json",
        json.dumps({"category": "refund"}),
        json.dumps({**valid_payload(), "category": "other"}),
        json.dumps({**valid_payload(), "priority": "critical"}),
        json.dumps({**valid_payload(), "sentiment": "angry"}),
        json.dumps({**valid_payload(), "needs_human_review": "false"}),
        json.dumps({**valid_payload(), "suggested_reply": {"text": "draft"}}),
        json.dumps({**valid_payload(), "suggested_reply": ""}),
        json.dumps({**valid_payload(), "extra": "not-allowed"}),
    ],
)
def test_invalid_structured_response_is_rejected(content: str) -> None:
    with pytest.raises(TriageProviderError):
        build_mapper().map(content)


def test_excessively_long_response_is_rejected() -> None:
    with pytest.raises(TriageProviderError):
        build_mapper().map("x" * (MAX_PROVIDER_RESPONSE_LENGTH + 1))
