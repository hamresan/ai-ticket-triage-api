from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Request, Response

from ai_ticket_triage.application.tickets.errors import TicketNotFoundError
from ai_ticket_triage.application.triage.dto import TriageTicketInput
from ai_ticket_triage.presentation.dependencies import TicketUseCases
from ai_ticket_triage.presentation.mappers import TicketPresentationMapper
from ai_ticket_triage.presentation.schemas import (
    CategoryQuery,
    CreateTicketRequest,
    PriorityQuery,
    TicketResponse,
    TicketStatusQuery,
)


def create_ticket_router(
    dependency: Callable[[], TicketUseCases],
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])
    ticket_use_cases_dependency = Depends(dependency)

    @router.post("", response_model=TicketResponse, status_code=201)
    async def create_ticket(
        request_body: CreateTicketRequest,
        request: Request,
        response: Response,
        idempotency_key: Annotated[
            str, Header(alias="Idempotency-Key", min_length=1, max_length=255)
        ],
        use_cases: TicketUseCases = ticket_use_cases_dependency,
    ) -> TicketResponse:
        create_input = TicketPresentationMapper.to_create_input(request_body, idempotency_key)
        creation = await use_cases.create.execute(create_input)
        ticket = creation.ticket
        if creation.created:
            ticket = await use_cases.triage.execute(TriageTicketInput(ticket_id=ticket.id))
        else:
            response.status_code = 200
        request.state.ticket_id = str(ticket.id)
        request.state.fallback_used = (
            ticket.decision is not None and ticket.decision.provenance.value == "fallback"
        )
        return TicketPresentationMapper.to_response(ticket)

    @router.get("/{ticket_id}", response_model=TicketResponse)
    async def get_ticket(
        ticket_id: UUID,
        request: Request,
        use_cases: TicketUseCases = ticket_use_cases_dependency,
    ) -> TicketResponse:
        ticket = await use_cases.get.execute(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        request.state.ticket_id = str(ticket.id)
        return TicketPresentationMapper.to_response(ticket)

    @router.get("", response_model=list[TicketResponse])
    async def list_tickets(
        status: TicketStatusQuery | None = None,
        category: CategoryQuery | None = None,
        priority: PriorityQuery | None = None,
        needs_human_review: bool | None = None,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        use_cases: TicketUseCases = ticket_use_cases_dependency,
    ) -> list[TicketResponse]:
        filters = TicketPresentationMapper.to_filter(
            status,
            category,
            priority,
            needs_human_review,
            offset,
            limit,
        )
        tickets = await use_cases.list.execute(filters)
        return [TicketPresentationMapper.to_response(ticket) for ticket in tickets]

    return router
