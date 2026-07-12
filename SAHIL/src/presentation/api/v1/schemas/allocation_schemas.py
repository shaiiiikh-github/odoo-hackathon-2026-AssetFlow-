from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from src.domain.entities.allocation import AllocationStatus, TransferStatus


class AllocateAssetRequest(BaseModel):
    holder_user_id: uuid.UUID | None = None
    holder_department_id: uuid.UUID | None = None
    expected_return_date: date | None = None

    @model_validator(mode="after")
    def one_holder_required(self) -> "AllocateAssetRequest":
        if self.holder_user_id is None and self.holder_department_id is None:
            raise ValueError("Either holder_user_id or holder_department_id must be provided.")
        return self


class ReturnAssetRequest(BaseModel):
    condition_notes: str | None = Field(default=None, max_length=1000)


class RequestTransferRequest(BaseModel):
    requested_for_user_id: uuid.UUID | None = None
    requested_for_department_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def one_target_required(self) -> "RequestTransferRequest":
        if self.requested_for_user_id is None and self.requested_for_department_id is None:
            raise ValueError("Either requested_for_user_id or requested_for_department_id must be provided.")
        return self


class ResolveTransferRequest(BaseModel):
    approve: bool
    notes: str | None = Field(default=None, max_length=1000)


class AllocationResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    holder_user_id: uuid.UUID | None
    holder_department_id: uuid.UUID | None
    allocated_by_user_id: uuid.UUID
    status: AllocationStatus
    expected_return_date: date | None
    allocated_at: datetime
    returned_at: datetime | None
    return_condition_notes: str | None

    model_config = {"from_attributes": True}


class TransferRequestResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    from_allocation_id: uuid.UUID
    requested_by_user_id: uuid.UUID
    requested_for_user_id: uuid.UUID | None
    requested_for_department_id: uuid.UUID | None
    status: TransferStatus
    requested_at: datetime
    resolved_by_user_id: uuid.UUID | None
    resolved_at: datetime | None
    resolution_notes: str | None

    model_config = {"from_attributes": True}
