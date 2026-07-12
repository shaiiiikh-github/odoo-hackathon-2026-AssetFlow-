from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.application.services.maintenance_service import MaintenanceService
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import EntityNotFoundError
from src.presentation.api.v1.schemas.maintenance_schemas import (
    AssignTechnicianRequest,
    MaintenanceRequestResponse,
    RaiseMaintenanceRequest,
    RejectMaintenanceRequest,
    ResolveMaintenanceRequest,
)
from src.presentation.dependencies import get_maintenance_service
from src.presentation.middleware.auth_middleware import require_any_authenticated, require_asset_manager_or_admin

router = APIRouter(tags=["Maintenance Management"])


@router.post(
    "/assets/{asset_id}/maintenance-requests",
    response_model=MaintenanceRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def raise_maintenance_request(
    asset_id: uuid.UUID,
    payload: RaiseMaintenanceRequest,
    acting_user: User = Depends(require_any_authenticated),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    """Any employee can raise a request (e.g. the current holder). Returns 409 if the asset already has an open request."""
    request = await service.raise_request(
        acting_user=acting_user,
        asset_id=asset_id,
        issue_description=payload.issue_description,
        priority=payload.priority,
        photo_url=payload.photo_url,
    )
    return MaintenanceRequestResponse.model_validate(request)


@router.get("/assets/{asset_id}/maintenance-requests", response_model=list[MaintenanceRequestResponse])
async def get_maintenance_history(
    asset_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> list[MaintenanceRequestResponse]:
    history = await service.get_history_for_asset(asset_id)
    return [MaintenanceRequestResponse.model_validate(r) for r in history]


@router.get("/maintenance-requests/{request_id}", response_model=MaintenanceRequestResponse)
async def get_maintenance_request(
    request_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    request = await service.get_request(request_id)
    if request is None:
        raise EntityNotFoundError("MaintenanceRequest", str(request_id))
    return MaintenanceRequestResponse.model_validate(request)


@router.post("/maintenance-requests/{request_id}/approve", response_model=MaintenanceRequestResponse)
async def approve_maintenance_request(
    request_id: uuid.UUID,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    """Approval is the cross-module trigger: the asset flips to UNDER_MAINTENANCE atomically with this approval."""
    request = await service.approve_request(acting_user=acting_user, request_id=request_id)
    return MaintenanceRequestResponse.model_validate(request)


@router.post("/maintenance-requests/{request_id}/reject", response_model=MaintenanceRequestResponse)
async def reject_maintenance_request(
    request_id: uuid.UUID,
    payload: RejectMaintenanceRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    request = await service.reject_request(acting_user=acting_user, request_id=request_id, reason=payload.reason)
    return MaintenanceRequestResponse.model_validate(request)


@router.post("/maintenance-requests/{request_id}/assign-technician", response_model=MaintenanceRequestResponse)
async def assign_technician(
    request_id: uuid.UUID,
    payload: AssignTechnicianRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    request = await service.assign_technician(
        acting_user=acting_user,
        request_id=request_id,
        technician_name=payload.technician_name,
        technician_contact=payload.technician_contact,
    )
    return MaintenanceRequestResponse.model_validate(request)


@router.post("/maintenance-requests/{request_id}/start-progress", response_model=MaintenanceRequestResponse)
async def start_progress(
    request_id: uuid.UUID,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    request = await service.start_progress(acting_user=acting_user, request_id=request_id)
    return MaintenanceRequestResponse.model_validate(request)


@router.post("/maintenance-requests/{request_id}/resolve", response_model=MaintenanceRequestResponse)
async def resolve_maintenance_request(
    request_id: uuid.UUID,
    payload: ResolveMaintenanceRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceRequestResponse:
    """Resolution is the second cross-module trigger: the asset flips back to AVAILABLE atomically with this call."""
    request = await service.resolve_request(
        acting_user=acting_user, request_id=request_id, resolution_notes=payload.resolution_notes
    )
    return MaintenanceRequestResponse.model_validate(request)
