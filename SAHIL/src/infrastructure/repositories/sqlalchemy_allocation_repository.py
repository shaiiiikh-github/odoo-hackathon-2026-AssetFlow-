from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_allocation_repository import IAllocationRepository
from src.domain.entities.allocation import Allocation, AllocationStatus, TransferRequest, TransferStatus
from src.infrastructure.database.models.allocation_model import AllocationModel
from src.infrastructure.database.models.transfer_request_model import TransferRequestModel


class SqlAlchemyAllocationRepository(IAllocationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- mapping helpers -------------------------------------------------
    @staticmethod
    def _to_entity(model: AllocationModel) -> Allocation:
        return Allocation(
            id=model.id,
            asset_id=model.asset_id,
            holder_user_id=model.holder_user_id,
            holder_department_id=model.holder_department_id,
            allocated_by_user_id=model.allocated_by_user_id,
            status=model.status,
            expected_return_date=model.expected_return_date,
            allocated_at=model.allocated_at,
            returned_at=model.returned_at,
            return_condition_notes=model.return_condition_notes,
        )

    @staticmethod
    def _transfer_to_entity(model: TransferRequestModel) -> TransferRequest:
        return TransferRequest(
            id=model.id,
            asset_id=model.asset_id,
            from_allocation_id=model.from_allocation_id,
            requested_by_user_id=model.requested_by_user_id,
            requested_for_user_id=model.requested_for_user_id,
            requested_for_department_id=model.requested_for_department_id,
            status=model.status,
            requested_at=model.requested_at,
            resolved_by_user_id=model.resolved_by_user_id,
            resolved_at=model.resolved_at,
            resolution_notes=model.resolution_notes,
        )

    # --- reads -------------------------------------------------------------
    async def get_active_for_asset(self, asset_id: UUID) -> Allocation | None:
        stmt = select(AllocationModel).where(
            AllocationModel.asset_id == asset_id, AllocationModel.status == AllocationStatus.ACTIVE
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_active_for_asset_for_update(self, asset_id: UUID) -> Allocation | None:
        # Row lock scoped to the (at most one) ACTIVE allocation row. Combined
        # with the asset row lock taken just before this in AllocationService,
        # this closes the "read active allocation -> decide -> write" window:
        # a second concurrent transaction requesting the same asset blocks
        # here until the first COMMITs or ROLLBACKs.
        stmt = (
            select(AllocationModel)
            .where(AllocationModel.asset_id == asset_id, AllocationModel.status == AllocationStatus.ACTIVE)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_history_for_asset(self, asset_id: UUID) -> list[Allocation]:
        stmt = (
            select(AllocationModel)
            .where(AllocationModel.asset_id == asset_id)
            .order_by(AllocationModel.allocated_at.desc())
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def get_overdue(self) -> list[Allocation]:
        today = datetime.utcnow().date()
        stmt = select(AllocationModel).where(
            AllocationModel.status == AllocationStatus.ACTIVE,
            AllocationModel.expected_return_date.is_not(None),
            AllocationModel.expected_return_date < today,
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    # --- writes --------------------------------------------------------------
    async def add(self, allocation: Allocation) -> Allocation:
        model = AllocationModel(
            id=allocation.id,
            asset_id=allocation.asset_id,
            holder_user_id=allocation.holder_user_id,
            holder_department_id=allocation.holder_department_id,
            allocated_by_user_id=allocation.allocated_by_user_id,
            status=allocation.status,
            expected_return_date=allocation.expected_return_date,
        )
        self._session.add(model)
        # flush (not commit) so the partial-unique-index check happens now,
        # inside the still-open transaction, while the caller still holds
        # the asset row lock — any violation surfaces as an IntegrityError
        # the service layer can translate cleanly.
        await self._session.flush()
        return self._to_entity(model)

    async def close(
        self, allocation_id: UUID, status: AllocationStatus, returned_at: datetime, notes: str | None
    ) -> None:
        model = await self._session.get(AllocationModel, allocation_id)
        if model is None:
            raise ValueError(f"Allocation {allocation_id} does not exist.")
        model.status = status
        model.returned_at = returned_at
        model.return_condition_notes = notes
        await self._session.flush()

    # --- transfer requests -----------------------------------------------
    async def add_transfer_request(self, transfer: TransferRequest) -> TransferRequest:
        model = TransferRequestModel(
            id=transfer.id,
            asset_id=transfer.asset_id,
            from_allocation_id=transfer.from_allocation_id,
            requested_by_user_id=transfer.requested_by_user_id,
            requested_for_user_id=transfer.requested_for_user_id,
            requested_for_department_id=transfer.requested_for_department_id,
            status=transfer.status,
        )
        self._session.add(model)
        await self._session.flush()
        return self._transfer_to_entity(model)

    async def get_transfer_request_for_update(self, transfer_request_id: UUID) -> TransferRequest | None:
        stmt = select(TransferRequestModel).where(TransferRequestModel.id == transfer_request_id).with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._transfer_to_entity(model) if model else None

    async def resolve_transfer_request(
        self, transfer_request_id: UUID, status: TransferStatus, resolved_by_user_id: UUID, notes: str | None
    ) -> None:
        model = await self._session.get(TransferRequestModel, transfer_request_id)
        if model is None:
            raise ValueError(f"Transfer request {transfer_request_id} does not exist.")
        model.status = status
        model.resolved_by_user_id = resolved_by_user_id
        model.resolved_at = datetime.utcnow()
        model.resolution_notes = notes
        await self._session.flush()
