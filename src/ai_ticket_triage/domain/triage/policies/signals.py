from dataclasses import dataclass

from ai_ticket_triage.domain.triage import Category


@dataclass(frozen=True, slots=True)
class TriageSignalDetector:
    signals: dict[Category, tuple[str, ...]]

    @classmethod
    def default(cls) -> "TriageSignalDetector":
        return cls(
            signals={
                Category.REFUND: ("refund", "money back", "charged twice", "duplicate charge"),
                Category.BILLING: ("billing", "invoice", "charge", "payment"),
                Category.ACCOUNT_ACCESS: ("locked out", "cannot log in", "can't log in", "password reset"),
                Category.TECHNICAL: ("error", "bug", "not working", "technical"),
                Category.ABUSIVE: ("idiot", "stupid", "useless", "hate you"),
            }
        )

    def detect(self, text: str) -> frozenset[Category]:
        normalized = text.casefold()
        return frozenset(
            category
            for category, phrases in self.signals.items()
            if any(phrase in normalized for phrase in phrases)
        )
