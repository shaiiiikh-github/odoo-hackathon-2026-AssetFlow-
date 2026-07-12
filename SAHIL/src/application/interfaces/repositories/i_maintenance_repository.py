from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.maintenance import MaintenanceRequest, MaintenanceStatus

# Requests in these states are "open" — an asset should have at most one.
OPEN_MAINTENANCE_STATUSES: frozenset[MaintenanceStatus] = frozenset(
    {
        MaintenanceStatus.PENDING,
        MaintenanceStatus.APPROVED,
        MaintenanceStatus.TECHNICIAN_ASSIGNED,
        MaintenanceStatus.IN_PROGRESS,
    }
)


class IMaintenanceRepository(ABC):
    @abstractmethod
    async def add(self, request: MaintenanceRequest) -> MaintenanceRequest:
        ...

    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> MaintenanceRequest | None:
        ...

    @abstractmethod
    async def get_by_id_for_update(self, request_id: UUID) -> MaintenanceRequest | None:
        """SELECT ... FOR UPDATE — serializes concurrent approve/assign/resolve calls on one request."""
        ...

    @abstractmethod
    async def get_open_for_asset(self, asset_id: UUID) -> MaintenanceRequest | None:
        ...

    @abstractmethod
    async def update(self, request: MaintenanceRequest) -> MaintenanceRequest:
        ...

    @abstractmethod
    async def get_history_for_asset(self, asset_id: UUID) -> list[MaintenanceRequest]:
        ...
