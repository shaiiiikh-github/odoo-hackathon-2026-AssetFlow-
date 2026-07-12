from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_maintenance_repository import (
    OPEN_MAINTENANCE_STATUSES,
    IMaintenanceRepository,
)
from src.domain.entities.maintenance import MaintenanceRequest
from src.infrastructure.database.models.maintenance_request_model import MaintenanceRequestModel


class SqlAlchemyMaintenanceRepository(IMaintenanceRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: MaintenanceRequestModel) -> MaintenanceRequest:
        return MaintenanceRequest(
            id=model.id,
            asset_id=model.asset_id,
            raised_by_user_id=model.raised_by_user_id,
            issue_description=model.issue_description,
            priority=model.priority,
            status=model.status,
            photo_url=model.photo_url,
            approved_by_user_id=model.approved_by_user_id,
            rejection_reason=model.rejection_reason,
            assigned_technician_name=model.assigned_technician_name,
            assigned_technician_contact=model.assigned_technician_contact,
            resolution_notes=model.resolution_notes,
            created_at=model.created_at,
            resolved_at=model.resolved_at,
        )

    async def add(self, request: MaintenanceRequest) -> MaintenanceRequest:
        model = MaintenanceRequestModel(
            id=request.id,
            asset_id=request.asset_id,
            raised_by_user_id=request.raised_by_user_id,
            issue_description=request.issue_description,
            priority=request.priority,
            status=request.status,
            photo_url=request.photo_url,
        )
        self._session.add(model)
        # flush now (not commit): if a second open request already exists
        # for this asset, uq_open_maintenance_per_asset fires here, inside
        # the still-open transaction, while the caller still holds whatever
        # locks it took — see MaintenanceService.raise_request.
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, request_id: UUID) -> MaintenanceRequest | None:
        model = await self._session.get(MaintenanceRequestModel, request_id)
        return self._to_entity(model) if model else None

    async def get_by_id_for_update(self, request_id: UUID) -> MaintenanceRequest | None:
        stmt = select(MaintenanceRequestModel).where(MaintenanceRequestModel.id == request_id).with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_open_for_asset(self, asset_id: UUID) -> MaintenanceRequest | None:
        stmt = select(MaintenanceRequestModel).where(
            MaintenanceRequestModel.asset_id == asset_id,
            MaintenanceRequestModel.status.in_(OPEN_MAINTENANCE_STATUSES),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, request: MaintenanceRequest) -> MaintenanceRequest:
        model = await self._session.get(MaintenanceRequestModel, request.id)
        if model is None:
            raise ValueError(f"Maintenance request {request.id} does not exist.")
        model.status = request.status
        model.approved_by_user_id = request.approved_by_user_id
        model.rejection_reason = request.rejection_reason
        model.assigned_technician_name = request.assigned_technician_name
        model.assigned_technician_contact = request.assigned_technician_contact
        model.resolution_notes = request.resolution_notes
        model.resolved_at = request.resolved_at
        await self._session.flush()
        return self._to_entity(model)

    async def get_history_for_asset(self, asset_id: UUID) -> list[MaintenanceRequest]:
        stmt = (
            select(MaintenanceRequestModel)
            .where(MaintenanceRequestModel.asset_id == asset_id)
            .order_by(MaintenanceRequestModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]
