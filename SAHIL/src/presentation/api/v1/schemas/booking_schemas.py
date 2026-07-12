from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from src.domain.entities.booking import BookingStatus


class CreateBookingRequest(BaseModel):
    start_time: datetime = Field(description="Timezone-aware start time (UTC recommended).")
    end_time: datetime = Field(description="Timezone-aware end time; must be after start_time.")
    department_id: uuid.UUID | None = None
    purpose: str | None = Field(default=None, max_length=500)


class BookingResponse(BaseModel):
    id: uuid.UUID
    asset_id: uuid.UUID
    booked_by_user_id: uuid.UUID
    department_id: uuid.UUID | None
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    purpose: str | None
    created_at: datetime
    cancelled_at: datetime | None

    model_config = {"from_attributes": True}
