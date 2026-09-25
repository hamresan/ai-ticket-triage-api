from ai_ticket_triage.domain.tickets import TicketStatus
from ai_ticket_triage.domain.triage import Category, Priority
from ai_ticket_triage.presentation.mappers import TicketPresentationMapper
from ai_ticket_triage.presentation.schemas import (
    CategoryQuery,
    PriorityQuery,
    TicketStatusQuery,
)


def test_ticket_query_maps_to_application_filter() -> None:
    filters = TicketPresentationMapper.to_filter(
        TicketStatusQuery.NEW,
        CategoryQuery.BILLING,
        PriorityQuery.HIGH,
        True,
        10,
        25,
    )

    assert filters.status is TicketStatus.NEW
    assert filters.category is Category.BILLING
    assert filters.priority is Priority.HIGH
    assert filters.needs_human_review is True
    assert filters.offset == 10
    assert filters.limit == 25


def test_missing_ticket_filters_map_to_default_query() -> None:
    filters = TicketPresentationMapper.to_filter(None, None, None, None, 0, 50)

    assert filters.status is None
    assert filters.category is None
    assert filters.priority is None
    assert filters.needs_human_review is None


def test_missing_decision_maps_to_none() -> None:
    assert TicketPresentationMapper.to_decision_response(None) is None
