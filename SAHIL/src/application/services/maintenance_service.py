from __future__ import annotations

import uuid
from datetime import datetime

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.asset import AssetStatus
from src.domain.entities.maintenance import MaintenancePriority, MaintenanceRequest, MaintenanceStatus
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import (
    DuplicateActiveMaintenanceRequestError,
    EntityNotFoundError,
    InsufficientPermissionError,
)
from src.domain.state_machines.asset_state_machine import AssetStateMachine
from src.domain.state_machines.maintenance_state_machine import MaintenanceStateMachine


class MaintenanceService:
    """
    Owns the maintenance workflow AND the two points where it reaches across
    module boundaries into the asset lifecycle:
      - approve_request(): flips the asset AVAILABLE/ALLOCATED -> UNDER_MAINTENANCE
      - resolve_request(): flips the asset UNDER_MAINTENANCE -> AVAILABLE

    Separation of concerns: this service imports AssetStateMachine (a pure,
    stateless domain rule) and mutates the asset entity itself directly —
    it does NOT import or call AssetService. That keeps the dependency graph
    a one-way arrow (maintenance -> asset), never asset -> maintenance, so
    there is no import cycle between the two application services. Both
    services are simply two different orchestrators that are each allowed
    to move an Asset entity through the SAME state machine and persist it
    via the SAME repository (`uow.assets`) — the state machine is the shared
    contract, not a shared service dependency.

    Concurrency: every mutating method locks the asset row (FOR UPDATE)
    before locking/reading the maintenance request row, in that fixed order
    — identical convention to AllocationService — so a maintenance approval
    can never race an allocation/return on the same asset into an
    inconsistent state.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ---------------------------------------------------------------- Raise
    async def raise_request(
        self,
        *,
        acting_user: User,
        asset_id: uuid.UUID,
        issue_description: str,
        priority: MaintenancePriority,
        photo_url: str | None,
    ) -> MaintenanceRequest:
        async with self._uow as uow:
            asset = await uow.assets.get_by_id_for_update(asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(asset_id))

            existing_open = await uow.maintenance.get_open_for_asset(asset_id)
            if existing_open is not None:
                raise DuplicateActiveMaintenanceRequestError(str(asset_id))

            request = MaintenanceRequest(
                id=uuid.uuid4(),
                asset_id=asset_id,
                raised_by_user_id=acting_user.id,
                issue_description=issue_description.strip(),
                priority=priority,
                status=MaintenanceStatus.PENDING,
                photo_url=photo_url,
            )
            try:
                created = await uow.maintenance.add(request)
            except Exception as exc:
                if _is_unique_violation(exc, "uq_open_maintenance_per_asset"):
                    raise DuplicateActiveMaintenanceRequestError(str(asset_id)) from exc
                raise
            await uow.commit()
            return created

    # ---------------------------------------------------------------- Approve / Reject
    async def approve_request(self, *, acting_user: User, request_id: uuid.UUID) -> MaintenanceRequest:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            request = await uow.maintenance.get_by_id_for_update(request_id)
            if request is None:
                raise EntityNotFoundError("MaintenanceRequest", str(request_id))

            # Lock the asset AFTER the request, mirroring the fixed
            # request-then-asset order used consistently for this workflow
            # (contrast with AllocationService, which locks asset-then-
            # allocation — the two workflows never lock the same two tables
            # in opposite order against each other, since only one of them
            # ever locks the maintenance_requests table at all).
            asset = await uow.assets.get_by_id_for_update(request.asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(request.asset_id))

            MaintenanceStateMachine.transition(request, MaintenanceStatus.APPROVED)
            request.approved_by_user_id = acting_user.id

            # The cross-module side effect: approval is what flips the core
            # asset status. If the asset is in a state that can't legally
            # move to UNDER_MAINTENANCE (e.g. it's already LOST or RETIRED),
            # AssetStateMachine raises InvalidStateTransitionError and the
            # whole transaction rolls back — the maintenance request is NOT
            # left dangling in an APPROVED state with no matching asset change.
            previous_asset_status = asset.status
            AssetStateMachine.transition(asset, AssetStatus.UNDER_MAINTENANCE)

            await uow.maintenance.update(request)
            await uow.assets.update(asset)
            await uow.assets.record_state_transition(
                asset_id=asset.id,
                from_state=previous_asset_status,
                to_state=AssetStatus.UNDER_MAINTENANCE,
                triggered_by_user_id=acting_user.id,
                reason=f"Maintenance request {request.id} approved",
            )
            await uow.commit()
            return request

    async def reject_request(self, *, acting_user: User, request_id: uuid.UUID, reason: str) -> MaintenanceRequest:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            request = await uow.maintenance.get_by_id_for_update(request_id)
            if request is None:
                raise EntityNotFoundError("MaintenanceRequest", str(request_id))

            MaintenanceStateMachine.transition(request, MaintenanceStatus.REJECTED)
            request.rejection_reason = reason.strip()
            # No asset-side effect on rejection — the asset was never moved
            # out of its current status while the request was PENDING.
            await uow.maintenance.update(request)
            await uow.commit()
            return request

    # ---------------------------------------------------------------- Technician assignment / progress
    async def assign_technician(
        self, *, acting_user: User, request_id: uuid.UUID, technician_name: str, technician_contact: str | None
    ) -> MaintenanceRequest:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            request = await uow.maintenance.get_by_id_for_update(request_id)
            if request is None:
                raise EntityNotFoundError("MaintenanceRequest", str(request_id))

            MaintenanceStateMachine.transition(request, MaintenanceStatus.TECHNICIAN_ASSIGNED)
            request.assigned_technician_name = technician_name.strip()
            request.assigned_technician_contact = technician_contact
            await uow.maintenance.update(request)
            await uow.commit()
            return request

    async def start_progress(self, *, acting_user: User, request_id: uuid.UUID) -> MaintenanceRequest:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            request = await uow.maintenance.get_by_id_for_update(request_id)
            if request is None:
                raise EntityNotFoundError("MaintenanceRequest", str(request_id))
            MaintenanceStateMachine.transition(request, MaintenanceStatus.IN_PROGRESS)
            await uow.maintenance.update(request)
            await uow.commit()
            return request

    # ---------------------------------------------------------------- Resolve
    async def resolve_request(
        self, *, acting_user: User, request_id: uuid.UUID, resolution_notes: str | None
    ) -> MaintenanceRequest:
        if not acting_user.can_manage_assets():
            raise InsufficientPermissionError(required_roles=["ADMIN", "ASSET_MANAGER"])

        async with self._uow as uow:
            request = await uow.maintenance.get_by_id_for_update(request_id)
            if request is None:
                raise EntityNotFoundError("MaintenanceRequest", str(request_id))

            asset = await uow.assets.get_by_id_for_update(request.asset_id)
            if asset is None:
                raise EntityNotFoundError("Asset", str(request.asset_id))

            MaintenanceStateMachine.transition(request, MaintenanceStatus.RESOLVED)
            request.resolution_notes = resolution_notes
            request.resolved_at = datetime.utcnow()

            # Second cross-module side effect: resolution returns the asset
            # to service. Same rollback-together guarantee as approval —
            # if the asset can't legally return to AVAILABLE (shouldn't
            # normally happen since APPROVED already put it into
            # UNDER_MAINTENANCE), the whole resolve() call fails atomically.
            AssetStateMachine.transition(asset, AssetStatus.AVAILABLE)

            await uow.maintenance.update(request)
            await uow.assets.update(asset)
            await uow.assets.record_state_transition(
                asset_id=asset.id,
                from_state=AssetStatus.UNDER_MAINTENANCE,
                to_state=AssetStatus.AVAILABLE,
                triggered_by_user_id=acting_user.id,
                reason=f"Maintenance request {request.id} resolved",
            )
            await uow.commit()
            return request

    # ---------------------------------------------------------------- Read-only queries
    async def get_request(self, request_id: uuid.UUID) -> MaintenanceRequest | None:
        async with self._uow as uow:
            return await uow.maintenance.get_by_id(request_id)

    async def get_history_for_asset(self, asset_id: uuid.UUID) -> list[MaintenanceRequest]:
        async with self._uow as uow:
            return await uow.maintenance.get_history_for_asset(asset_id)


def _is_unique_violation(exc: Exception, index_hint: str) -> bool:
    message = str(getattr(exc, "orig", exc)).lower()
    return "unique" in message and index_hint.lower() in message
