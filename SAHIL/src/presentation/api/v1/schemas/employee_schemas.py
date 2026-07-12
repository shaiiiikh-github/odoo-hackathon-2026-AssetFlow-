from __future__ import annotations

import uuid

from pydantic import BaseModel

from src.domain.entities.user import UserStatus


class SetEmployeeStatusRequest(BaseModel):
    status: UserStatus


class EmployeeListQuery(BaseModel):
    department_id: uuid.UUID | None = None
    search: str | None = None
