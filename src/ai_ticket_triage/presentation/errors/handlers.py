from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ai_ticket_triage.application.tickets.errors import (
    IdempotencyConflictError,
    TicketNotFoundError,
)


def error_response(
    request: Request, *, status_code: int, code: str, message: str
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {"code": code, "message": message},
            "request_id": str(request.state.request_id),
        },
    )


def register_error_handlers(application: FastAPI) -> None:
    @application.exception_handler(RequestValidationError)
    async def validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return error_response(
            request,
            status_code=422,
            code="validation_error",
            message="Request validation failed.",
        )

    @application.exception_handler(TicketNotFoundError)
    async def ticket_not_found(
        request: Request, exc: TicketNotFoundError
    ) -> JSONResponse:
        return error_response(
            request,
            status_code=404,
            code="ticket_not_found",
            message="Ticket not found.",
        )

    @application.exception_handler(IdempotencyConflictError)
    async def idempotency_conflict(
        request: Request, exc: IdempotencyConflictError
    ) -> JSONResponse:
        return error_response(
            request,
            status_code=409,
            code="idempotency_conflict",
            message="Idempotency key was already used for a different request.",
        )

    @application.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        return error_response(
            request,
            status_code=500,
            code="internal_error",
            message="An unexpected error occurred.",
        )
