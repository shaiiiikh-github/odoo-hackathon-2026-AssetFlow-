from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from src.domain.entities.audit import AuditCycleStatus, AuditFindingStatus


class CreateAuditCycleRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    department_id: uuid.UUID | None = None
    location: str | None = Field(default=None, max_length=255)
    start_date: date
    end_date: date
    auditor_user_ids: list[uuid.UUID] = Field(default_factory=list, min_length=1)

    @model_validator(mode="after")
    def dates_ordered(self) -> "CreateAuditCycleRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date.")
        return self


class AssignAuditorRequest(BaseModel):
    auditor_user_id: uuid.UUID


class SubmitFindingRequest(BaseModel):
    asset_id: uuid.UUID
    finding_status: AuditFindingStatus
    notes: str | None = Field(default=None, max_length=1000)


class AuditCycleResponse(BaseModel):
    id: uuid.UUID
    name: str
    department_id: uuid.UUID | None
    location: str | None
    start_date: date
    end_date: date
    status: AuditCycleStatus
    created_by_user_id: uuid.UUID
    created_at: datetime
    closed_by_user_id: uuid.UUID | None
    closed_at: datetime | None

    model_config = {"from_attributes": True}


class AuditFindingResponse(BaseModel):
    id: uuid.UUID
    cycle_id: uuid.UUID
    asset_id: uuid.UUID
    marked_by_user_id: uuid.UUID
    status: AuditFindingStatus
    notes: str | None
    marked_at: datetime

    model_config = {"from_attributes": True}


class DiscrepancyReportEntryResponse(BaseModel):
    asset_id: uuid.UUID
    asset_tag: str
    finding_status: AuditFindingStatus
    marked_by_user_id: uuid.UUID
    notes: str | None
    marked_at: datetime

    model_config = {"from_attributes": True}
