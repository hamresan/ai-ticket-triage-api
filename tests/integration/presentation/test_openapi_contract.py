from pathlib import Path

import pytest

from tests.integration.presentation.support import build_client


def test_openapi_matches_public_ticket_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)

    response = client.get("/openapi.json")

    assert response.status_code == 200
    document = response.json()
    paths = document["paths"]

    assert set(("/health", "/api/v1/tickets", "/api/v1/tickets/{ticket_id}")) <= set(paths)

    create = paths["/api/v1/tickets"]["post"]
    parameters = {parameter["name"]: parameter for parameter in create["parameters"]}
    assert parameters["Idempotency-Key"]["in"] == "header"
    assert parameters["Idempotency-Key"]["required"] is True
    assert {"200", "201", "409", "422"} <= set(create["responses"])

    listing = paths["/api/v1/tickets"]["get"]
    query_parameters = {
        parameter["name"]
        for parameter in listing["parameters"]
        if parameter["in"] == "query"
    }
    assert query_parameters == {
        "status",
        "category",
        "priority",
        "needs_human_review",
        "offset",
        "limit",
    }
    assert "422" in listing["responses"]

    retrieve = paths["/api/v1/tickets/{ticket_id}"]["get"]
    assert {"200", "404", "422"} <= set(retrieve["responses"])


def test_openapi_error_responses_use_public_error_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client = build_client(tmp_path, monkeypatch)

    document = client.get("/openapi.json").json()
    schemas = document["components"]["schemas"]

    error_schema = schemas["ErrorResponse"]
    assert set(error_schema["required"]) == {"error", "request_id"}
    detail_schema = schemas["ErrorDetailResponse"]
    assert set(detail_schema["required"]) == {"code", "message"}
