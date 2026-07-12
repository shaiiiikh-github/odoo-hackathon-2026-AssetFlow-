from __future__ import annotations

from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.infrastructure.database.session import AsyncSessionFactory
from src.infrastructure.repositories.sqlalchemy_allocation_repository import SqlAlchemyAllocationRepository
from src.infrastructure.repositories.sqlalchemy_asset_repository import SqlAlchemyAssetRepository
from src.infrastructure.repositories.sqlalchemy_audit_repository import SqlAlchemyAuditRepository
from src.infrastructure.repositories.sqlalchemy_booking_repository import SqlAlchemyBookingRepository
from src.infrastructure.repositories.sqlalchemy_category_repository import SqlAlchemyCategoryRepository
from src.infrastructure.repositories.sqlalchemy_department_repository import SqlAlchemyDepartmentRepository
from src.infrastructure.repositories.sqlalchemy_maintenance_repository import SqlAlchemyMaintenanceRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """
    Owns ONE session and ONE transaction per 'async with' block.
    Every service call that mutates state wraps its work in:

        async with self._uow as uow:
            ...
            await uow.commit()

    On any unhandled exception inside the block, __aexit__ rolls back automatically —
    services never need to remember to roll back manually.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession] = AsyncSessionFactory) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(self._session)
        self.departments = SqlAlchemyDepartmentRepository(self._session)
        self.categories = SqlAlchemyCategoryRepository(self._session)
        self.assets = SqlAlchemyAssetRepository(self._session)
        self.allocations = SqlAlchemyAllocationRepository(self._session)
        self.bookings = SqlAlchemyBookingRepository(self._session)
        self.maintenance = SqlAlchemyMaintenanceRepository(self._session)
        self.audits = SqlAlchemyAuditRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        try:
            if exc_type is not None:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        assert self._session is not None
        await self._session.commit()

    async def rollback(self) -> None:
        assert self._session is not None
        await self._session.rollback()
