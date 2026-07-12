from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from app.domain.enums import AssetStatus, AssetCondition

class AssetBase(BaseModel):
    serial_number: str
    category_id: UUID
    condition: AssetCondition = AssetCondition.GOOD
    is_shared_bookable: bool = False
    location: Optional[str] = None
    acquisition_cost: Optional[float] = None
    acquisition_date: Optional[date] = None

class AssetCreate(AssetBase):
    pass

class AssetStatusUpdate(BaseModel):
    status: AssetStatus

class AssetResponse(AssetBase):
    id: UUID
    asset_tag: str
    status: AssetStatus
    created_at: datetime

    class Config:
        from_attributes = True