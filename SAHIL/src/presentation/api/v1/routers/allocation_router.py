from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.application.services.allocation_service import AllocationService
from src.domain.entities.user import User
from src.presentation.api.v1.schemas.allocation_schemas import (
    AllocateAssetRequest,
    AllocationResponse,
    RequestTransferRequest,
    ResolveTransferRequest,
    ReturnAssetRequest,
    TransferRequestResponse,
)
from src.presentation.dependencies import get_allocation_service
from src.presentation.middleware.auth_middleware import (
    require_any_authenticated,
    require_asset_manager_or_admin,
    require_department_head_or_above,
)

router = APIRouter(tags=["Asset Allocation & Transfer"])


@router.post("/assets/{asset_id}/allocate", response_model=AllocationResponse, status_code=status.HTTP_201_CREATED)
async def allocate_asset(
    asset_id: uuid.UUID,
    payload: AllocateAssetRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationResponse:
    """
    Direct allocation. Returns 409 with the current holder's identity if the
    asset is already allocated — the conflict rule from Screen 5. Use
    POST /assets/{asset_id}/transfer-requests instead in that case.
    """
    allocation = await service.allocate_asset(
        acting_user=acting_user,
        asset_id=asset_id,
        holder_user_id=payload.holder_user_id,
        holder_department_id=payload.holder_department_id,
        expected_return_date=payload.expected_return_date,
    )
    return AllocationResponse.model_validate(allocation)


@router.post("/assets/{asset_id}/return", response_model=AllocationResponse)
async def return_asset(
    asset_id: uuid.UUID,
    payload: ReturnAssetRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationResponse:
    allocation = await service.return_asset(
        acting_user=acting_user, asset_id=asset_id, condition_notes=payload.condition_notes
    )
    return AllocationResponse.model_validate(allocation)


@router.get("/assets/{asset_id}/allocations", response_model=list[AllocationResponse])
async def get_allocation_history(
    asset_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    service: AllocationService = Depends(get_allocation_service),
) -> list[AllocationResponse]:
    history = await service.get_allocation_history(asset_id)
    return [AllocationResponse.model_validate(a) for a in history]


@router.get("/allocations/overdue", response_model=list[AllocationResponse])
async def get_overdue_allocations(
    _: User = Depends(require_any_authenticated),
    service: AllocationService = Depends(get_allocation_service),
) -> list[AllocationResponse]:
    """Feeds the Dashboard's overdue-returns KPI and the Notifications screen."""
    overdue = await service.get_overdue_allocations()
    return [AllocationResponse.model_validate(a) for a in overdue]


@router.post(
    "/assets/{asset_id}/transfer-requests",
    response_model=TransferRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_transfer(
    asset_id: uuid.UUID,
    payload: RequestTransferRequest,
    acting_user: User = Depends(require_any_authenticated),
    service: AllocationService = Depends(get_allocation_service),
) -> TransferRequestResponse:
    """Any authenticated holder can request a transfer of an asset currently allocated to them."""
    transfer = await service.request_transfer(
        acting_user=acting_user,
        asset_id=asset_id,
        requested_for_user_id=payload.requested_for_user_id,
        requested_for_department_id=payload.requested_for_department_id,
    )
    return TransferRequestResponse.model_validate(transfer)


@router.post("/transfer-requests/{transfer_request_id}/resolve", response_model=TransferRequestResponse)
async def resolve_transfer(
    transfer_request_id: uuid.UUID,
    payload: ResolveTransferRequest,
    acting_user: User = Depends(require_department_head_or_above),
    service: AllocationService = Depends(get_allocation_service),
) -> TransferRequestResponse:
    """Approve or reject — approval atomically closes the old allocation and opens a new one."""
    transfer = await service.resolve_transfer(
        acting_user=acting_user,
        transfer_request_id=transfer_request_id,
        approve=payload.approve,
        notes=payload.notes,
    )
    return TransferRequestResponse.model_validate(transfer)
