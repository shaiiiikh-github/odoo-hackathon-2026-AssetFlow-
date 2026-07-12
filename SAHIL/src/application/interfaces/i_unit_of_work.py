from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType

from src.application.interfaces.repositories.i_allocation_repository import IAllocationRepository
from src.application.interfaces.repositories.i_asset_repository import IAssetRepository
from src.application.interfaces.repositories.i_audit_repository import IAuditRepository
from src.application.interfaces.repositories.i_booking_repository import IBookingRepository
from src.application.interfaces.repositories.i_department_repository import IDepartmentRepository
from src.application.interfaces.repositories.i_category_repository import ICategoryRepository
from src.application.interfaces.repositories.i_maintenance_repository import IMaintenanceRepository
from src.application.interfaces.repositories.i_user_repository import IUserRepository


class IUnitOfWork(ABC):
    """
    Defines a single atomic transaction boundary spanning one or more repositories.
    Services depend on THIS interface, never on a concrete SQLAlchemy session directly —
    keeps the application layer persistence-agnostic and easy to test with an in-memory fake.
    """

    users: IUserRepository
    departments: IDepartmentRepository
    categories: ICategoryRepository
    assets: IAssetRepository
    allocations: IAllocationRepository
    bookings: IBookingRepository
    maintenance: IMaintenanceRepository
    audits: IAuditRepository

    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork":
        ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...
