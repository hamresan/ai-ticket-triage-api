from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from ai_ticket_triage.presentation.dependencies import TicketUseCases
from ai_ticket_triage.presentation.mappers import TicketPresentationMapper
from ai_ticket_triage.presentation.schemas import (
    CreateTicketRequest,
    TicketResponse,
    TicketStatusQuery,
)


def create_ticket_router(
    dependency: Callable[[], TicketUseCases],
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])

    @router.post("", response_model=TicketResponse, status_code=201)
    async def create_ticket(
        request_body: CreateTicketRequest,
        use_cases: TicketUseCases = Depends(dependency),
    ) -> TicketResponse:
        create_input = TicketPresentationMapper.to_create_input(request_body)
        ticket = await use_cases.create.execute(create_input)
        return TicketPresentationMapper.to_response(ticket)

    @router.get("/{ticket_id}", response_model=TicketResponse)
    async def get_ticket(
        ticket_id: UUID,
        request: Request,
        use_cases: TicketUseCases = Depends(dependency),
    ) -> TicketResponse | JSONResponse:
        ticket = await use_cases.get.execute(ticket_id)
        if ticket is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {"code": "ticket_not_found", "message": "Ticket not found."},
                    "request_id": str(request.state.request_id),
                },
            )
        return TicketPresentationMapper.to_response(ticket)

    @router.get("", response_model=list[TicketResponse])
    async def list_tickets(
        status: TicketStatusQuery | None = None,
        use_cases: TicketUseCases = Depends(dependency),
    ) -> list[TicketResponse]:
        filters = TicketPresentationMapper.to_filter(status)
        tickets = await use_cases.list.execute(filters)
        return [TicketPresentationMapper.to_response(ticket) for ticket in tickets]

    return router
