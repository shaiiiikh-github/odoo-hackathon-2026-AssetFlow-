from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions.domain_exceptions import (
    AssetAlreadyAllocatedError,
    AssetNotBookableError,
    AssetNotInAuditScopeError,
    AuditCycleClosedError,
    BookingNotCancellableError,
    DepartmentHierarchyCycleError,
    DepartmentInUseError,
    DomainError,
    DuplicateActiveMaintenanceRequestError,
    DuplicateAssetTagError,
    DuplicateCategoryNameError,
    DuplicateEmailError,
    DuplicateSerialNumberError,
    EntityNotFoundError,
    InactiveAccountError,
    InsufficientPermissionError,
    InvalidBookingWindowError,
    InvalidCategoryError,
    InvalidCredentialsError,
    InvalidMaintenanceTransitionError,
    InvalidRolePromotionError,
    InvalidStateTransitionError,
    NoActiveAllocationError,
    NotAnAssignedAuditorError,
    SlotOverlapError,
    TransferRequestNotPendingError,
)

_STATUS_MAP: dict[type[DomainError], int] = {
    EntityNotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateEmailError: status.HTTP_409_CONFLICT,
    DuplicateCategoryNameError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    InactiveAccountError: status.HTTP_403_FORBIDDEN,
    InsufficientPermissionError: status.HTTP_403_FORBIDDEN,
    InvalidRolePromotionError: status.HTTP_400_BAD_REQUEST,
    DepartmentHierarchyCycleError: status.HTTP_400_BAD_REQUEST,
    DepartmentInUseError: status.HTTP_409_CONFLICT,
    DuplicateSerialNumberError: status.HTTP_409_CONFLICT,
    DuplicateAssetTagError: status.HTTP_409_CONFLICT,
    InvalidStateTransitionError: status.HTTP_400_BAD_REQUEST,
    InvalidCategoryError: status.HTTP_400_BAD_REQUEST,
    # Phase 3: allocation & booking
    AssetAlreadyAllocatedError: status.HTTP_409_CONFLICT,
    NoActiveAllocationError: status.HTTP_400_BAD_REQUEST,
    TransferRequestNotPendingError: status.HTTP_409_CONFLICT,
    AssetNotBookableError: status.HTTP_400_BAD_REQUEST,
    SlotOverlapError: status.HTTP_409_CONFLICT,
    InvalidBookingWindowError: status.HTTP_400_BAD_REQUEST,
    BookingNotCancellableError: status.HTTP_409_CONFLICT,
    # Phase 4: maintenance & audits
    InvalidMaintenanceTransitionError: status.HTTP_400_BAD_REQUEST,
    DuplicateActiveMaintenanceRequestError: status.HTTP_409_CONFLICT,
    AuditCycleClosedError: status.HTTP_409_CONFLICT,
    NotAnAssignedAuditorError: status.HTTP_403_FORBIDDEN,
    AssetNotInAuditScopeError: status.HTTP_400_BAD_REQUEST,
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        http_status = _STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=http_status, content={"detail": str(exc)})
