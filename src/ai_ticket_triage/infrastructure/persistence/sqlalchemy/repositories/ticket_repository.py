from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ai_ticket_triage.application.tickets.dto.ticket_query import TicketFilter
from ai_ticket_triage.application.tickets.ports import TicketRepository
from ai_ticket_triage.domain.tickets import Ticket
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.mappers import TicketMapper
from ai_ticket_triage.infrastructure.persistence.sqlalchemy.models import TicketModel


class SqlAlchemyTicketRepository(TicketRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def add(self, ticket: Ticket) -> None:
        async with self._session_factory() as session:
            session.add(TicketMapper.to_model(ticket))
            await session.commit()

    async def update(self, ticket: Ticket) -> None:
        async with self._session_factory() as session:
            await session.merge(TicketMapper.to_model(ticket))
            await session.commit()

    async def get_by_id(self, ticket_id: UUID) -> Ticket | None:
        async with self._session_factory() as session:
            model = await session.get(TicketModel, ticket_id)
            return TicketMapper.to_domain(model) if model is not None else None

    async def list(self, filters: TicketFilter) -> tuple[Ticket, ...]:
        statement = select(TicketModel).order_by(TicketModel.created_at, TicketModel.id)
        if filters.status is not None:
            statement = statement.where(TicketModel.status == filters.status.value)
        async with self._session_factory() as session:
            models = (await session.scalars(statement)).all()
            return tuple(TicketMapper.to_domain(model) for model in models)
