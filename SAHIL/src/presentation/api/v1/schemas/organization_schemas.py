from __future__ import annotations

import uuid
from typing import Any

from pydantic import BaseModel, Field

from src.domain.entities.department import DepartmentStatus


class DepartmentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    parent_department_id: uuid.UUID | None = None
    head_user_id: uuid.UUID | None = None


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    parent_department_id: uuid.UUID | None = None
    head_user_id: uuid.UUID | None = None
    status: DepartmentStatus | None = None


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: DepartmentStatus
    parent_department_id: uuid.UUID | None
    head_user_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    custom_fields_schema: dict[str, Any] = Field(default_factory=dict)


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    custom_fields_schema: dict[str, Any] | None = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    custom_fields_schema: dict[str, Any]

    model_config = {"from_attributes": True}
