from __future__ import annotations

import uuid
from datetime import date, datetime

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.allocation import Allocation, AllocationStatus, TransferRequest, TransferStatus
from src.domain.entities.asset import AssetStatus
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import (
    AssetAlreadyAllocatedError,
    EntityNotFoundError,
    InsufficientPermissionError,
    NoActiveAllocationError,
    TransferRequestNotPendingError,
)
from src.domain.state_machines.asset_state_machine import AssetStateMachine


class AllocationService:
    """
    Owns allocation, return, and transfer-request workflows.

    Concurrency strategy (see AssetFlow Phase 3 design notes):
      1. Every mutating method opens ONE Unit-of-Work transaction and, as its
         FIRST DB call, takes a `SELECT ... FOR UPDATE` lock on the asset row
         via `uow.assets.get_by_id_for_update(...)`. This lock is the
         serialization point: a second concurrent request for the same asset
         blocks at that SELECT until the first transaction commits or rolls
         back — it does not proceed to read a stale status.
      2. Only after the lock is held do we read/write the ACTIVE allocation
         row (also FOR UPDATE, for symmetry and to protect the return/
         transfer paths where the asset itself might already be back to
         AVAILABLE conceptually but the allocation row is what we're
         actually racing on).
      3. A partial unique index (`uq_active_allocation_per_asset`, DB-level,
         see migration 0003) is the final backstop in case any code path
         ever manages to skip step 1 — it turns what would otherwise be a
         silent double-allocation into a hard IntegrityError we can catch.
      4. We deliberately do NOT rely on SERIALIZABLE isolation + retry loops
         here. Row-level FOR UPDATE locks give us the same correctness for
         this access pattern (single hot row per operation) with none of the
         retry-on-serialization-failure complexity, and — importantly — they
         don't block unrelated assets from being allocated concurrently,
         since the lock is per-row, not table- or transaction-wide.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ---------------------------------------------------------------- Allocate
    async def allocate_asset(
        self,
        *,
        acting_user: User,
        asset_id: uuid.UUID,
        holder_user_id: uuid.UUID | None,
        holder_department_id: uuid.UUID | None,
        expected_return_date: date | None,
    ) -> Allocation:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            # Step 1: lock the asset row FIRST. Every other method in this
            # service also locks the asset before the allocation, in this
            # same order, so two different operations racing on the same
            # asset (e.g. allocate vs. return) can never deadlock each other
            # by acquiring locks in reversed order.
            asset = await uow.assets.get_by_id_for_update(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            if asset.status == AssetStatus.ALLOCATED:
                current = await uow.allocations.get_active_for_asset(asset_id)
                raise AssetAlreadyAllocatedError(
                    asset_id=str(asset_id),
                    current_holder_user_id=str(current.holder_user_id) if current and current.holder_user_id else None,
                    current_holder_department_id=(
                        str(current.holder_department_id) if current and current.holder_department_id else None
                    ),
                )

            # Any other status (RESERVED, UNDER_MAINTENANCE, LOST, RETIRED,
            # DISPOSED) is rejected by the state machine below with a clear
            # InvalidStateTransitionError — we don't special-case them here.
            AssetStateMachine.transition(asset, AssetStatus.ALLOCATED)

            allocation = Allocation(
                id=uuid.uuid4(),
                asset_id=asset_id,
                holder_user_id=holder_user_id,
                holder_department_id=holder_department_id,
                allocated_by_user_id=acting_user.id,
                status=AllocationStatus.ACTIVE,
                expected_return_date=expected_return_date,
            )

            try:
                created = await uow.allocations.add(allocation)
            except Exception as exc:
                # Backstop: uq_active_allocation_per_asset firing means our
                # own FOR UPDATE lock somehow didn't cover this path (e.g. a
                # future code change bypassing it) — translate rather than
                # leak a raw IntegrityError.
                if _is_unique_violation(exc, "uq_active_allocation_per_asset"):
                    raise AssetAlreadyAllocatedError(str(asset_id), None, None) from exc
                raise

            await uow.assets.update(asset)
            await uow.assets.record_state_transition(
                asset_id=asset_id,
                from_state=AssetStatus.AVAILABLE,
                to_state=AssetStatus.ALLOCATED,
                triggered_by_user_id=acting_user.id,
                reason="Direct allocation",
            )
            await uow.commit()
            return created

    # ---------------------------------------------------------------- Return
    async def return_asset(
        self, *, acting_user: User, asset_id: uuid.UUID, condition_notes: str | None
    ) -> Allocation:
        async with self._uow as uow:
            asset = await uow.assets.get_by_id_for_update(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            active = await uow.allocations.get_active_for_asset_for_update(asset_id)
            if active is None:
                raise NoActiveAllocationError(str(asset_id))

            AssetStateMachine.transition(asset, AssetStatus.AVAILABLE)
            asset.department_id = None

            await uow.allocations.close(
                allocation_id=active.id,
                status=AllocationStatus.RETURNED,
                returned_at=datetime.utcnow(),
                notes=condition_notes,
            )
            await uow.assets.update(asset)
            await uow.assets.record_state_transition(
                asset_id=asset_id,
                from_state=AssetStatus.ALLOCATED,
                to_state=AssetStatus.AVAILABLE,
                triggered_by_user_id=acting_user.id,
                reason="Returned",
            )
            await uow.commit()
            active.status = AllocationStatus.RETURNED
            return active

    # ---------------------------------------------------------------- Transfer: request
    async def request_transfer(
        self,
        *,
        acting_user: User,
        asset_id: uuid.UUID,
        requested_for_user_id: uuid.UUID | None,
        requested_for_department_id: uuid.UUID | None,
    ) -> TransferRequest:
        async with self._uow as uow:
            # Locking the asset here isn't strictly required for correctness
            # (uq_pending_transfer_per_allocation is the real guard against
            # duplicate REQUESTED rows), but it keeps this method consistent
            # with the "lock asset first" convention and avoids racing the
            # allocate/return paths on the same asset mid-request.
            asset = await uow.assets.get_by_id_for_update(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            active = await uow.allocations.get_active_for_asset(asset_id)
            if active is None:
                raise NoActiveAllocationError(str(asset_id))

            transfer = TransferRequest(
                id=uuid.uuid4(),
                asset_id=asset_id,
                from_allocation_id=active.id,
                requested_by_user_id=acting_user.id,
                requested_for_user_id=requested_for_user_id,
                requested_for_department_id=requested_for_department_id,
                status=TransferStatus.REQUESTED,
            )
            created = await uow.allocations.add_transfer_request(transfer)
            await uow.commit()
            return created

    # ---------------------------------------------------------------- Transfer: approve/reject
    async def resolve_transfer(
        self,
        *,
        acting_user: User,
        transfer_request_id: uuid.UUID,
        approve: bool,
        notes: str | None,
    ) -> TransferRequest:
        if not acting_user.can_manage_assets() and acting_user.role.value != "DEPARTMENT_HEAD":
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER", "DEPARTMENT_HEAD"])

        async with self._uow as uow:
            transfer = await uow.allocations.get_transfer_request_for_update(transfer_request_id)
            if transfer is None:
                raise EntityNotFoundError("TransferRequest", str(transfer_request_id))
            if transfer.status != TransferStatus.REQUESTED:
                raise TransferRequestNotPendingError(str(transfer_request_id))

            # Lock the asset for the duration of the approval so it can't be
            # concurrently returned/re-allocated out from under this transfer.
            asset = await uow.assets.get_by_id_for_update(transfer.asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(transfer.asset_id))

            new_status = TransferStatus.APPROVED if approve else TransferStatus.REJECTED
            await uow.allocations.resolve_transfer_request(
                transfer_request_id=transfer_request_id,
                status=new_status,
                resolved_by_user_id=acting_user.id,
                notes=notes,
            )

            if approve:
                # Close the old allocation as TRANSFERRED (not RETURNED — it
                # was never idle) and open a new ACTIVE one. Two writes, one
                # transaction: history stays gap-free and the partial unique
                # index never sees two ACTIVE rows at once because the old
                # one's status flips before the new one is inserted.
                await uow.allocations.close(
                    allocation_id=transfer.from_allocation_id,
                    status=AllocationStatus.TRANSFERRED,
                    returned_at=datetime.utcnow(),
                    notes="Superseded by approved transfer",
                )
                new_allocation = Allocation(
                    id=uuid.uuid4(),
                    asset_id=transfer.asset_id,
                    holder_user_id=transfer.requested_for_user_id,
                    holder_department_id=transfer.requested_for_department_id,
                    allocated_by_user_id=acting_user.id,
                    status=AllocationStatus.ACTIVE,
                )
                await uow.allocations.add(new_allocation)
                # Asset stays ALLOCATED throughout — only the holder changes —
                # so no state-machine transition is fired here, only the
                # holder-facing department_id convenience field updates.
                asset.department_id = transfer.requested_for_department_id
                await uow.assets.update(asset)

            await uow.commit()
            transfer.status = new_status
            return transfer

    # ---------------------------------------------------------------- Read-only queries
    async def get_allocation_history(self, asset_id: uuid.UUID) -> list[Allocation]:
        async with self._uow as uow:
            return await uow.allocations.get_history_for_asset(asset_id)

    async def get_active_allocation(self, asset_id: uuid.UUID) -> Allocation | None:
        async with self._uow as uow:
            return await uow.allocations.get_active_for_asset(asset_id)

    async def get_overdue_allocations(self) -> list[Allocation]:
        async with self._uow as uow:
            return await uow.allocations.get_overdue()


def _is_unique_violation(exc: Exception, index_hint: str) -> bool:
    message = str(getattr(exc, "orig", exc)).lower()
    return "unique" in message and index_hint.lower() in message
