from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.infrastructure.database.models import Base

class AllocationStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"
    TRANSFER_REQUESTED = "TRANSFER_REQUESTED"

class BookingStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class AssetAllocation(Base):
    __tablename__ = "asset_allocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    
    # Can be allocated to a specific user OR a department
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_to_dept_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    
    allocated_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(AllocationStatus), default=AllocationStatus.ACTIVE, nullable=False)
    
    allocated_at = Column(DateTime(timezone=True), server_default=func.now())
    expected_return_date = Column(DateTime(timezone=True), nullable=True)
    actual_return_date = Column(DateTime(timezone=True), nullable=True)
    return_condition_notes = Column(Text, nullable=True)

    # Relationships
    asset = relationship("Asset", back_populates="allocations")

class ResourceBooking(Base):
    __tablename__ = "resource_bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    booked_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    status = Column(Enum(BookingStatus), default=BookingStatus.UPCOMING, nullable=False)

    # Relationships
    asset = relationship("Asset", back_populates="bookings")