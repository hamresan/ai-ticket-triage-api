import json

from ai_ticket_triage.infrastructure.providers.structured.contracts import TriageTaskInputV1

TRIAGE_PROMPT_VERSION = "v1"


class TriagePromptBuilder:
    def build(self, task_input: TriageTaskInputV1) -> str:
        payload = json.dumps(
            {"subject": task_input.subject, "message": task_input.message},
            ensure_ascii=False,
        )
        return (
            "You triage customer-support tickets. Return JSON only. "
            "Required fields: category, priority, sentiment, needs_human_review, "
            "suggested_reply. "
            "category must be one of refund, billing, account_access, technical, abusive, "
            "unknown. priority must be one of low, medium, high, urgent. "
            "sentiment must be one of positive, neutral, negative, frustrated. "
            "suggested_reply must be a non-empty draft reply string. "
            f"Prompt version: {TRIAGE_PROMPT_VERSION}. Ticket: {payload}"
        )
