from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Enum, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.infrastructure.database.models import Base
from app.domain.enums import AssetStatus, AssetCondition

class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_tag = Column(String(50), unique=True, index=True, nullable=False)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("asset_categories.id"), nullable=False)
    
    status = Column(Enum(AssetStatus), default=AssetStatus.AVAILABLE, nullable=False)
    condition = Column(Enum(AssetCondition), default=AssetCondition.GOOD, nullable=False)
    
    is_shared_bookable = Column(Boolean, default=False, nullable=False)
    location = Column(String(255), nullable=True)
    acquisition_cost = Column(Numeric(10, 2), nullable=True)
    acquisition_date = Column(Date, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    category = relationship("AssetCategory", backref="assets")
    allocations = relationship("AssetAllocation", back_populates="asset")
    bookings = relationship("ResourceBooking", back_populates="asset")