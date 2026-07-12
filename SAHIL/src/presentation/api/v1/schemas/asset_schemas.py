from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from src.domain.entities.asset import AssetCondition, AssetStatus


class AssetRegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category_id: uuid.UUID
    serial_number: str = Field(min_length=1, max_length=255)
    condition: AssetCondition = AssetCondition.NEW
    location: str = Field(min_length=1, max_length=255)
    is_bookable: bool = False
    acquisition_date: date | None = None
    acquisition_cost: Decimal | None = Field(default=None, ge=0)
    department_id: uuid.UUID | None = None
    photo_url: str | None = None
    document_urls: list[str] = Field(default_factory=list)

    @field_validator("serial_number")
    @classmethod
    def serial_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Serial number cannot be blank.")
        return v.strip()


class AssetUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    condition: AssetCondition | None = None
    location: str | None = Field(default=None, min_length=1, max_length=255)
    is_bookable: bool | None = None
    department_id: uuid.UUID | None = None
    photo_url: str | None = None
    document_urls: list[str] | None = None


class AssetTransitionRequest(BaseModel):
    to_state: AssetStatus
    reason: str | None = Field(default=None, max_length=500)


class AssetResponse(BaseModel):
    id: uuid.UUID
    asset_tag: str
    serial_number: str
    name: str
    category_id: uuid.UUID
    status: AssetStatus
    condition: AssetCondition
    location: str
    is_bookable: bool
    acquisition_date: date | None
    acquisition_cost: Decimal | None
    department_id: uuid.UUID | None
    photo_url: str | None
    document_urls: list[str]

    model_config = {"from_attributes": True}


class AssetSearchResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int


class AssetStateTransitionResponse(BaseModel):
    id: uuid.UUID
    from_state: AssetStatus
    to_state: AssetStatus
    triggered_by_user_id: uuid.UUID
    reason: str | None
    created_at: datetime
