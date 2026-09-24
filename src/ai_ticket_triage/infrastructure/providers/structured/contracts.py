from dataclasses import dataclass


TRIAGE_CONTRACT_VERSION = "v1"


@dataclass(frozen=True, slots=True)
class TriageTaskInputV1:
    subject: str
    message: str


@dataclass(frozen=True, slots=True)
class TriageTaskOutputV1:
    category: str
    priority: str
    sentiment: str
    needs_human_review: bool
    suggested_reply: str
