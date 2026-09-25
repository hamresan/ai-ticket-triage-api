import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from tests.integration.presentation.support import build_client


def test_sequential_idempotent_replay_does_not_repeat_triage(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    payload = {"subject": "Refund", "message": "Please refund my order."}
    headers = {"Idempotency-Key": "sequential-replay"}

    first = client.post("/api/v1/tickets", json=payload, headers=headers)
    second = client.post("/api/v1/tickets", json=payload, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json() == first.json()
    listed = client.get("/api/v1/tickets")
    assert len(listed.json()) == 1


def test_idempotency_key_reuse_with_different_payload_is_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    headers = {"Idempotency-Key": "conflict-key"}
    first = client.post(
        "/api/v1/tickets",
        json={"subject": "First", "message": "First body"},
        headers=headers,
    )
    conflict = client.post(
        "/api/v1/tickets",
        json={"subject": "Second", "message": "Different body"},
        headers=headers,
    )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "idempotency_conflict"
    assert conflict.json()["request_id"] == conflict.headers["X-Request-ID"]


def test_idempotency_key_is_required(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    client = build_client(tmp_path, monkeypatch)

    response = client.post(
        "/api/v1/tickets",
        json={"subject": "Subject", "message": "Body"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_concurrent_duplicate_requests_create_one_ticket(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    payload = {"subject": "Concurrent", "message": "Only one ticket should exist."}
    headers = {"Idempotency-Key": "concurrent-key"}

    def create() -> int:
        return client.post("/api/v1/tickets", json=payload, headers=headers).status_code

    with ThreadPoolExecutor(max_workers=2) as executor:
        statuses = list(executor.map(lambda _: create(), range(2)))

    assert sorted(statuses) == [200, 201]
    listed = client.get("/api/v1/tickets")
    assert len(listed.json()) == 1


def test_filters_ordering_and_pagination_are_deterministic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)
    for index in range(3):
        response = client.post(
            "/api/v1/tickets",
            json={"subject": f"Ticket {index}", "message": "Technical issue"},
            headers={"Idempotency-Key": f"query-{index}"},
        )
        assert response.status_code == 201

    all_tickets = client.get("/api/v1/tickets").json()
    matching = client.get(
        "/api/v1/tickets",
        params={
            "status": "triaged",
            "category": "technical",
            "priority": "medium",
            "needs_human_review": "false",
        },
    )
    page = client.get("/api/v1/tickets", params={"offset": 1, "limit": 1})

    assert matching.status_code == 200
    assert [item["id"] for item in matching.json()] == [item["id"] for item in all_tickets]
    assert [item["id"] for item in page.json()] == [all_tickets[1]["id"]]
    assert client.get("/api/v1/tickets", params={"category": "billing"}).json() == []


@pytest.mark.parametrize(
    ("name", "value"),
    [("offset", "-1"), ("limit", "0"), ("limit", "101"), ("priority", "invalid")],
)
def test_invalid_query_parameters_use_validation_policy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    name: str,
    value: str,
) -> None:
    client = build_client(tmp_path, monkeypatch)

    response = client.get("/api/v1/tickets", params={name: value})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_structured_logs_include_safe_metadata_without_sensitive_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO, logger="ai_ticket_triage.request")
    client = build_client(tmp_path, monkeypatch)
    sensitive_subject = "PRIVATE-SUBJECT-7788"
    sensitive_message = "PRIVATE-MESSAGE-9911"
    secret_key = "PRIVATE-IDEMPOTENCY-KEY"

    response = client.post(
        "/api/v1/tickets",
        json={"subject": sensitive_subject, "message": sensitive_message},
        headers={
            "Idempotency-Key": secret_key,
            "X-Request-ID": "safe-request-id",
        },
    )

    assert response.status_code == 201
    log_text = caplog.text
    assert sensitive_subject not in log_text
    assert sensitive_message not in log_text
    assert secret_key not in log_text
    event = json.loads(caplog.records[-1].message)
    assert event["request_id"] == "safe-request-id"
    assert event["ticket_id"] == response.json()["id"]
    assert event["provider"] == "fake"
    assert event["model"] is None
    assert event["fallback_used"] is False
    assert event["duration_ms"] >= 0
