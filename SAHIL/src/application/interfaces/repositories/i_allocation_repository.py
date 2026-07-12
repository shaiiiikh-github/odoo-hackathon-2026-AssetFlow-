from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from datetime import datetime

from src.domain.entities.allocation import Allocation, AllocationStatus, TransferRequest, TransferStatus


class IAllocationRepository(ABC):
    @abstractmethod
    async def get_active_for_asset(self, asset_id: UUID) -> Allocation | None:
        """Plain read — no lock. Used for display (Screen 4/5), not for the allocate/return decision path."""
        ...

    @abstractmethod
    async def get_active_for_asset_for_update(self, asset_id: UUID) -> Allocation | None:
        """
        Row-locking read: takes a FOR UPDATE lock on the active allocation row
        if one exists. Must be called from inside the same transaction that
        already locked the parent asset row — see AllocationService for why
        both locks are taken in a fixed order.
        """
        ...

    @abstractmethod
    async def add(self, allocation: Allocation) -> Allocation:
        ...

    @abstractmethod
    async def close(
        self, allocation_id: UUID, status: AllocationStatus, returned_at: datetime, notes: str | None
    ) -> None:
        ...

    @abstractmethod
    async def get_history_for_asset(self, asset_id: UUID) -> list[Allocation]:
        ...

    @abstractmethod
    async def get_overdue(self) -> list[Allocation]:
        ...

    # --- Transfer requests ---------------------------------------------------
    @abstractmethod
    async def add_transfer_request(self, transfer: TransferRequest) -> TransferRequest:
        ...

    @abstractmethod
    async def get_transfer_request_for_update(self, transfer_request_id: UUID) -> TransferRequest | None:
        ...

    @abstractmethod
    async def resolve_transfer_request(
        self, transfer_request_id: UUID, status: TransferStatus, resolved_by_user_id: UUID, notes: str | None
    ) -> None:
        ...
