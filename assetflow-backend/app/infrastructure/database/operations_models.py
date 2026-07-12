from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.infrastructure.database.models import Base
from app.domain.enums import MaintenancePriority, MaintenanceStatus, AuditCycleStatus, AuditItemStatus

class MaintenanceRequest(Base):
    __tablename__ = "maintenance_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    requested_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    priority = Column(Enum(MaintenancePriority), default=MaintenancePriority.MEDIUM, nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING, nullable=False)
    
    issue_description = Column(Text, nullable=False)
    
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    asset = relationship("Asset")

class AuditCycle(Base):
    __tablename__ = "audit_cycles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    status = Column(Enum(AuditCycleStatus), default=AuditCycleStatus.OPEN, nullable=False)
    
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    items = relationship("AuditItem", back_populates="audit_cycle", cascade="all, delete-orphan")

class AuditItem(Base):
    __tablename__ = "audit_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_cycle_id = Column(UUID(as_uuid=True), ForeignKey("audit_cycles.id"), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=False)
    verified_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    status = Column(Enum(AuditItemStatus), default=AuditItemStatus.PENDING, nullable=False)
    discrepancy_notes = Column(Text, nullable=True)
    
    verified_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    audit_cycle = relationship("AuditCycle", back_populates="items")
    asset = relationship("Asset")