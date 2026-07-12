from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_asset_repository import (
    AssetSearchFilters,
    AssetSearchResult,
    IAssetRepository,
)
from src.domain.entities.asset import Asset, AssetCondition, AssetStatus
from src.domain.value_objects.asset_tag import AssetTag
from src.infrastructure.database.models.asset_model import AssetModel
from src.infrastructure.database.models.asset_state_transition_model import AssetStateTransitionModel


class SqlAlchemyAssetRepository(IAssetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- mapping helpers -------------------------------------------------
    @staticmethod
    def _to_entity(model: AssetModel) -> Asset:
        return Asset(
            id=model.id,
            asset_tag=model.asset_tag,
            serial_number=model.serial_number,
            name=model.name,
            category_id=model.category_id,
            status=model.status,
            condition=model.condition,
            location=model.location,
            is_bookable=model.is_bookable,
            acquisition_date=model.acquisition_date,
            acquisition_cost=model.acquisition_cost,
            department_id=model.department_id,
            photo_url=model.photo_url,
            document_urls=list(model.document_urls or []),
            created_at=model.created_at,
        )

    # --- interface implementation ----------------------------------------
    async def add(self, asset: Asset) -> Asset:
        model = AssetModel(
            id=asset.id,
            asset_tag=asset.asset_tag,
            serial_number=asset.serial_number,
            name=asset.name,
            category_id=asset.category_id,
            status=asset.status,
            condition=asset.condition,
            location=asset.location,
            is_bookable=asset.is_bookable,
            acquisition_date=asset.acquisition_date,
            acquisition_cost=asset.acquisition_cost,
            department_id=asset.department_id,
            photo_url=asset.photo_url,
            document_urls=asset.document_urls,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, asset_id: UUID) -> Asset | None:
        model = await self._session.get(AssetModel, asset_id)
        return self._to_entity(model) if model else None

    async def get_by_id_for_update(self, asset_id: UUID) -> Asset | None:
        stmt = select(AssetModel).where(AssetModel.id == asset_id).with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_serial_number(self, serial_number: str) -> Asset | None:
        stmt = select(AssetModel).where(AssetModel.serial_number == serial_number)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_asset_tag(self, asset_tag: str) -> Asset | None:
        stmt = select(AssetModel).where(AssetModel.asset_tag == asset_tag)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def search(self, filters: AssetSearchFilters) -> AssetSearchResult:
        """
        Optimized search: every filterable column (asset_tag, serial_number,
        category_id, status, department_id) has a matching index (see
        AssetModel + Alembic migration), so this compiles to index scans
        rather than sequential scans even as the assets table grows into
        the tens of thousands of rows typical for an enterprise deployment.
        """
        stmt = select(AssetModel)
        count_stmt = select(func.count()).select_from(AssetModel)

        conditions = []
        if filters.asset_tag:
            conditions.append(AssetModel.asset_tag.ilike(f"%{filters.asset_tag}%"))
        if filters.serial_number:
            conditions.append(AssetModel.serial_number.ilike(f"%{filters.serial_number}%"))
        if filters.category_id:
            conditions.append(AssetModel.category_id == filters.category_id)
        if filters.status:
            conditions.append(AssetModel.status == filters.status)
        if filters.department_id:
            conditions.append(AssetModel.department_id == filters.department_id)
        if filters.location:
            conditions.append(AssetModel.location.ilike(f"%{filters.location}%"))
        if filters.is_bookable is not None:
            conditions.append(AssetModel.is_bookable == filters.is_bookable)

        for condition in conditions:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total_result = await self._session.execute(count_stmt)
        total = total_result.scalar_one()

        offset = (filters.page - 1) * filters.page_size
        stmt = stmt.order_by(AssetModel.created_at.desc()).offset(offset).limit(filters.page_size)

        result = await self._session.execute(stmt)
        items = [self._to_entity(m) for m in result.scalars().all()]

        return AssetSearchResult(items=items, total=total, page=filters.page, page_size=filters.page_size)

    async def update(self, asset: Asset) -> Asset:
        model = await self._session.get(AssetModel, asset.id)
        if model is None:
            raise ValueError(f"Asset {asset.id} does not exist and cannot be updated.")
        model.name = asset.name
        model.category_id = asset.category_id
        model.status = asset.status
        model.condition = asset.condition
        model.location = asset.location
        model.is_bookable = asset.is_bookable
        model.department_id = asset.department_id
        model.photo_url = asset.photo_url
        model.document_urls = asset.document_urls
        model.acquisition_cost = asset.acquisition_cost
        model.acquisition_date = asset.acquisition_date
        await self._session.flush()
        return self._to_entity(model)

    async def next_asset_tag(self) -> str:
        # nextval() on a Postgres SEQUENCE is atomic and race-safe under
        # concurrent transactions — this is the load-bearing guarantee that
        # prevents two simultaneous registrations from colliding on AF-0001.
        result = await self._session.execute(select(func.nextval("asset_tag_seq")))
        sequence_value = result.scalar_one()
        return AssetTag.format(sequence_value)

    async def record_state_transition(
        self, asset_id: UUID, from_state: AssetStatus, to_state: AssetStatus, triggered_by_user_id: UUID, reason: str | None
    ) -> None:
        entry = AssetStateTransitionModel(
            asset_id=asset_id,
            from_state=from_state,
            to_state=to_state,
            triggered_by_user_id=triggered_by_user_id,
            reason=reason,
        )
        self._session.add(entry)
        await self._session.flush()

    async def get_state_history(self, asset_id: UUID) -> list[dict]:
        stmt = (
            select(AssetStateTransitionModel)
            .where(AssetStateTransitionModel.asset_id == asset_id)
            .order_by(AssetStateTransitionModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [
            {
                "id": row.id,
                "from_state": row.from_state,
                "to_state": row.to_state,
                "triggered_by_user_id": row.triggered_by_user_id,
                "reason": row.reason,
                "created_at": row.created_at,
            }
            for row in result.scalars().all()
        ]
