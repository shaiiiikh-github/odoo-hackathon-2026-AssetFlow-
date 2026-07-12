from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_category_repository import ICategoryRepository
from src.domain.entities.asset_category import AssetCategory
from src.infrastructure.database.models.asset_category_model import AssetCategoryModel


class SqlAlchemyCategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: AssetCategoryModel) -> AssetCategory:
        return AssetCategory(
            id=model.id,
            name=model.name,
            custom_fields_schema=model.custom_fields_schema or {},
            created_at=model.created_at,
        )

    async def add(self, category: AssetCategory) -> AssetCategory:
        model = AssetCategoryModel(
            id=category.id, name=category.name, custom_fields_schema=category.custom_fields_schema
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, category_id: UUID) -> AssetCategory | None:
        model = await self._session.get(AssetCategoryModel, category_id)
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> AssetCategory | None:
        stmt = select(AssetCategoryModel).where(AssetCategoryModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self) -> list[AssetCategory]:
        stmt = select(AssetCategoryModel).order_by(AssetCategoryModel.name)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, category: AssetCategory) -> AssetCategory:
        model = await self._session.get(AssetCategoryModel, category.id)
        if model is None:
            raise ValueError(f"Category {category.id} does not exist and cannot be updated.")
        model.name = category.name
        model.custom_fields_schema = category.custom_fields_schema
        await self._session.flush()
        return self._to_entity(model)
