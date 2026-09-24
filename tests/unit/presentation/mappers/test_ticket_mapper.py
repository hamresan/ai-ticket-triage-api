from ai_ticket_triage.domain.tickets import TicketStatus
from ai_ticket_triage.presentation.mappers import TicketPresentationMapper
from ai_ticket_triage.presentation.schemas import TicketStatusQuery


def test_ticket_status_query_maps_to_application_filter() -> None:
    filters = TicketPresentationMapper.to_filter(TicketStatusQuery.NEW)

    assert filters.status is TicketStatus.NEW


def test_missing_ticket_status_maps_to_unfiltered_query() -> None:
    filters = TicketPresentationMapper.to_filter(None)

    assert filters.status is None


def test_missing_decision_maps_to_none() -> None:
    assert TicketPresentationMapper.to_decision_response(None) is None
