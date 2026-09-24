from ai_ticket_triage.infrastructure.providers.structured import (
    TRIAGE_CONTRACT_VERSION,
    TRIAGE_PROMPT_VERSION,
    TriagePromptBuilder,
    TriageTaskInputV1,
)


def test_v1_prompt_contains_contract_rules_and_ticket_payload() -> None:
    prompt = TriagePromptBuilder().build(
        TriageTaskInputV1(subject="Refund", message="Please refund order 42.")
    )

    assert TRIAGE_PROMPT_VERSION == "v1"
    assert TRIAGE_CONTRACT_VERSION == "v1"
    assert "Return JSON only" in prompt
    assert '"subject": "Refund"' in prompt
    assert '"message": "Please refund order 42."' in prompt
    assert "needs_human_review" in prompt
