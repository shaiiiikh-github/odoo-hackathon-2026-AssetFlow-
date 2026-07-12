from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from src.domain.entities.asset import Asset, AssetStatus


@dataclass
class AssetSearchFilters:
    asset_tag: str | None = None          # partial match
    serial_number: str | None = None      # partial match
    category_id: UUID | None = None
    status: AssetStatus | None = None
    department_id: UUID | None = None
    location: str | None = None
    is_bookable: bool | None = None
    page: int = 1
    page_size: int = 25


@dataclass
class AssetSearchResult:
    items: list[Asset]
    total: int
    page: int
    page_size: int


class IAssetRepository(ABC):
    @abstractmethod
    async def add(self, asset: Asset) -> Asset:
        ...

    @abstractmethod
    async def get_by_id(self, asset_id: UUID) -> Asset | None:
        ...

    @abstractmethod
    async def get_by_id_for_update(self, asset_id: UUID) -> Asset | None:
        """SELECT ... FOR UPDATE — used during state transitions to serialize concurrent writers."""
        ...

    @abstractmethod
    async def get_by_serial_number(self, serial_number: str) -> Asset | None:
        ...

    @abstractmethod
    async def get_by_asset_tag(self, asset_tag: str) -> Asset | None:
        ...

    @abstractmethod
    async def search(self, filters: AssetSearchFilters) -> AssetSearchResult:
        ...

    @abstractmethod
    async def update(self, asset: Asset) -> Asset:
        ...

    @abstractmethod
    async def next_asset_tag(self) -> str:
        """
        Atomically reserves the next asset tag using a DB sequence
        (nextval is race-safe under concurrent transactions — two Asset
        Managers registering assets simultaneously can never receive the
        same tag, unlike a 'SELECT MAX(...) + 1' approach).
        """
        ...

    @abstractmethod
    async def record_state_transition(
        self, asset_id: UUID, from_state: AssetStatus, to_state: AssetStatus, triggered_by_user_id: UUID, reason: str | None
    ) -> None:
        ...

    @abstractmethod
    async def get_state_history(self, asset_id: UUID) -> list[dict]:
        ...
