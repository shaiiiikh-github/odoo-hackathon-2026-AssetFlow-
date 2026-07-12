from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status

from src.application.interfaces.repositories.i_asset_repository import AssetSearchFilters
from src.application.services.asset_service import AssetService
from src.domain.entities.asset import AssetStatus
from src.domain.entities.user import User
from src.presentation.api.v1.schemas.asset_schemas import (
    AssetRegisterRequest,
    AssetResponse,
    AssetSearchResponse,
    AssetStateTransitionResponse,
    AssetTransitionRequest,
    AssetUpdateRequest,
)
from src.presentation.dependencies import get_asset_service
from src.presentation.middleware.auth_middleware import require_any_authenticated, require_asset_manager_or_admin

router = APIRouter(prefix="/assets", tags=["Asset Registration & Directory"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def register_asset(
    payload: AssetRegisterRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """
    Registers a new asset as AVAILABLE with an auto-generated Asset Tag.
    Duplicate serial numbers are rejected with 409 Conflict (see
    AssetService.register_asset for the two-layer duplicate check).
    """
    asset = await asset_service.register_asset(
        acting_user=acting_user,
        name=payload.name,
        category_id=payload.category_id,
        serial_number=payload.serial_number,
        condition=payload.condition,
        location=payload.location,
        is_bookable=payload.is_bookable,
        acquisition_date=payload.acquisition_date,
        acquisition_cost=payload.acquisition_cost,
        department_id=payload.department_id,
        photo_url=payload.photo_url,
        document_urls=payload.document_urls,
    )
    return AssetResponse.model_validate(asset)


@router.get("", response_model=AssetSearchResponse)
async def search_assets(
    asset_tag: str | None = Query(default=None, description="Partial match on Asset Tag, e.g. 'AF-01'"),
    serial_number: str | None = Query(default=None, description="Partial match on Serial Number"),
    category_id: uuid.UUID | None = None,
    status_filter: AssetStatus | None = Query(default=None, alias="status"),
    department_id: uuid.UUID | None = None,
    location: str | None = None,
    is_bookable: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    _: User = Depends(require_any_authenticated),
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetSearchResponse:
    """
    Indexed search across Asset Tag, Serial Number, Category, Status,
    Department, and Location. Every filter here maps to an indexed column
    (see AssetModel) so this stays fast as the catalog scales.
    """
    filters = AssetSearchFilters(
        asset_tag=asset_tag,
        serial_number=serial_number,
        category_id=category_id,
        status=status_filter,
        department_id=department_id,
        location=location,
        is_bookable=is_bookable,
        page=page,
        page_size=page_size,
    )
    result = await asset_service.search_assets(filters)
    return AssetSearchResponse(
        items=[AssetResponse.model_validate(a) for a in result.items],
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    asset = await asset_service.get_asset(asset_id)
    return AssetResponse.model_validate(asset)


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: uuid.UUID,
    payload: AssetUpdateRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Edits descriptive fields only — status can ONLY change via /assets/{id}/transition."""
    asset = await asset_service.update_asset_details(
        acting_user=acting_user,
        asset_id=asset_id,
        name=payload.name,
        condition=payload.condition,
        location=payload.location,
        is_bookable=payload.is_bookable,
        department_id=payload.department_id,
        photo_url=payload.photo_url,
        document_urls=payload.document_urls,
    )
    return AssetResponse.model_validate(asset)


@router.post("/{asset_id}/transition", response_model=AssetResponse)
async def transition_asset(
    asset_id: uuid.UUID,
    payload: AssetTransitionRequest,
    acting_user: User = Depends(require_asset_manager_or_admin),
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """
    Moves the asset to `to_state` if — and only if — the state machine
    permits that edge. Illegal moves (e.g. DISPOSED -> ALLOCATED) return
    400 with an explicit message; they never partially apply.
    """
    asset = await asset_service.transition_asset_status(
        acting_user=acting_user, asset_id=asset_id, to_state=payload.to_state, reason=payload.reason
    )
    return AssetResponse.model_validate(asset)


@router.get("/{asset_id}/history", response_model=list[AssetStateTransitionResponse])
async def get_asset_history(
    asset_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    asset_service: AssetService = Depends(get_asset_service),
) -> list[AssetStateTransitionResponse]:
    history = await asset_service.get_state_history(asset_id)
    return [AssetStateTransitionResponse(**entry) for entry in history]
