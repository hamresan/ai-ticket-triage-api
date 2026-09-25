import hashlib


class TicketRequestFingerprint:
    def create(self, subject: str, message: str) -> str:
        payload = f"{len(subject)}:{subject}{len(message)}:{message}".encode()
        return hashlib.sha256(payload).hexdigest()
