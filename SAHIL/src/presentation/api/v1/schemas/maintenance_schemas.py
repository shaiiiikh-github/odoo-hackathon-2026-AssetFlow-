from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entities.maintenance import MaintenancePriority, MaintenanceStatus


class RaiseMaintenanceRequest(BaseModel):
    issue_description: str = Field(min_length=1, max_length=2000)
    priority: MaintenancePriority = MaintenancePriority.MEDIUM
    photo_url: str | None = None


class RejectMaintenanceRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=1000)


class AssignTechnicianRequest(BaseModel):
    technician_name: str = Field(min_length=1, max_length=255)
    technician_contact: str | None = Field(default=None, max_length=255)


class ResolveMaintenanceRequest(BaseModel):
    resolution_notes: str | None = Field(default=None, max_length=1000)


class MaintenanceRequestResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    raised_by_user_id: uuid.UUID
    issue_description: str
    priority: MaintenancePriority
    status: MaintenanceStatus
    photo_url: str | None
    approved_by_user_id: uuid.UUID | None
    rejection_reason: str | None
    assigned_technician_name: str | None
    assigned_technician_contact: str | None
    resolution_notes: str | None
    created_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}
