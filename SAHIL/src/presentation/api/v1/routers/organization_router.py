from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.application.services.organization_service import OrganizationService
from src.domain.entities.department import DepartmentStatus
from src.domain.entities.user import User
from src.presentation.api.v1.schemas.organization_schemas import (
    CategoryCreateRequest,
    CategoryResponse,
    CategoryUpdateRequest,
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
)
from src.presentation.dependencies import get_organization_service
from src.presentation.middleware.auth_middleware import require_admin, require_any_authenticated

router = APIRouter(prefix="/organization", tags=["Organization Setup"])


# ---------------------------------------------------------------- Departments (Tab A)
@router.post(
    "/departments",
    response_model=DepartmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[],
)
async def create_department(
    payload: DepartmentCreateRequest,
    acting_user: User = Depends(require_admin),
    org_service: OrganizationService = Depends(get_organization_service),
) -> DepartmentResponse:
    department = await org_service.create_department(
        acting_user=acting_user,
        name=payload.name,
        parent_department_id=payload.parent_department_id,
        head_user_id=payload.head_user_id,
    )
    return DepartmentResponse.model_validate(department)


@router.patch("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: uuid.UUID,
    payload: DepartmentUpdateRequest,
    acting_user: User = Depends(require_admin),
    org_service: OrganizationService = Depends(get_organization_service),
) -> DepartmentResponse:
    department = await org_service.update_department(
        acting_user=acting_user,
        department_id=department_id,
        name=payload.name,
        parent_department_id=payload.parent_department_id,
        head_user_id=payload.head_user_id,
        status=payload.status,
    )
    return DepartmentResponse.model_validate(department)


@router.get("/departments", response_model=list[DepartmentResponse])
async def list_departments(
    status_filter: DepartmentStatus | None = None,
    _: User = Depends(require_any_authenticated),
    org_service: OrganizationService = Depends(get_organization_service),
) -> list[DepartmentResponse]:
    departments = await org_service.list_departments(status=status_filter)
    return [DepartmentResponse.model_validate(d) for d in departments]


@router.get("/departments/{department_id}", response_model=DepartmentResponse)
async def get_department(
    department_id: uuid.UUID,
    _: User = Depends(require_any_authenticated),
    org_service: OrganizationService = Depends(get_organization_service),
) -> DepartmentResponse:
    department = await org_service.get_department(department_id)
    return DepartmentResponse.model_validate(department)


# ---------------------------------------------------------------- Asset Categories (Tab B)
@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreateRequest,
    acting_user: User = Depends(require_admin),
    org_service: OrganizationService = Depends(get_organization_service),
) -> CategoryResponse:
    category = await org_service.create_category(
        acting_user=acting_user, name=payload.name, custom_fields_schema=payload.custom_fields_schema
    )
    return CategoryResponse.model_validate(category)


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    payload: CategoryUpdateRequest,
    acting_user: User = Depends(require_admin),
    org_service: OrganizationService = Depends(get_organization_service),
) -> CategoryResponse:
    category = await org_service.update_category(
        acting_user=acting_user,
        category_id=category_id,
        name=payload.name,
        custom_fields_schema=payload.custom_fields_schema,
    )
    return CategoryResponse.model_validate(category)


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    _: User = Depends(require_any_authenticated),
    org_service: OrganizationService = Depends(get_organization_service),
) -> list[CategoryResponse]:
    categories = await org_service.list_categories()
    return [CategoryResponse.model_validate(c) for c in categories]
