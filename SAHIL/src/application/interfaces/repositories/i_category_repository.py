from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.asset_category import AssetCategory


class ICategoryRepository(ABC):
    @abstractmethod
    async def add(self, category: AssetCategory) -> AssetCategory:
        ...

    @abstractmethod
    async def get_by_id(self, category_id: UUID) -> AssetCategory | None:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> AssetCategory | None:
        ...

    @abstractmethod
    async def list_all(self) -> list[AssetCategory]:
        ...

    @abstractmethod
    async def update(self, category: AssetCategory) -> AssetCategory:
        ...
