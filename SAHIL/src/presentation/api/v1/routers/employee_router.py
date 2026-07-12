from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from src.application.services.employee_directory_service import EmployeeDirectoryService
from src.domain.entities.user import Role, User
from src.presentation.api.v1.schemas.auth_schemas import UserResponse
from src.presentation.api.v1.schemas.employee_schemas import SetEmployeeStatusRequest
from src.presentation.dependencies import get_employee_directory_service
from src.presentation.middleware.auth_middleware import require_admin

router = APIRouter(prefix="/organization/employees", tags=["Employee Directory"])


@router.get("", response_model=list[UserResponse])
async def list_employees(
    role: Role | None = None,
    department_id: uuid.UUID | None = None,
    search: str | None = None,
    acting_user: User = Depends(require_admin),
    directory_service: EmployeeDirectoryService = Depends(get_employee_directory_service),
) -> list[UserResponse]:
    employees = await directory_service.list_employees(
        acting_user=acting_user, role=role, department_id=department_id, search=search
    )
    return [UserResponse.model_validate(e) for e in employees]


@router.patch("/{user_id}/status", response_model=UserResponse)
async def set_employee_status(
    user_id: uuid.UUID,
    payload: SetEmployeeStatusRequest,
    acting_user: User = Depends(require_admin),
    directory_service: EmployeeDirectoryService = Depends(get_employee_directory_service),
) -> UserResponse:
    updated = await directory_service.set_employee_status(
        acting_user=acting_user, target_user_id=user_id, status=payload.status
    )
    return UserResponse.model_validate(updated)
