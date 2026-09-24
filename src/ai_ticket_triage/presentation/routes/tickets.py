from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.domain.tickets import TicketStatus
from ai_ticket_triage.presentation.mappers import TicketPresentationMapper
from ai_ticket_triage.presentation.schemas import CreateTicketRequest, TicketResponse

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=201)
async def create_ticket(request_body: CreateTicketRequest, request: Request) -> TicketResponse:
    create_input = TicketPresentationMapper.to_create_input(request_body)
    ticket = await request.app.state.create_ticket.execute(create_input)
    return TicketPresentationMapper.to_response(ticket)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: UUID, request: Request) -> TicketResponse | JSONResponse:
    ticket = await request.app.state.get_ticket.execute(ticket_id)
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
    request: Request,
    status: TicketStatus | None = None,
) -> list[TicketResponse]:
    tickets = await request.app.state.list_tickets.execute(TicketFilter(status=status))
    return [TicketPresentationMapper.to_response(ticket) for ticket in tickets]
