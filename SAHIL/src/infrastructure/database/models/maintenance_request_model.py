from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.maintenance import MaintenancePriority, MaintenanceStatus
from src.infrastructure.database.models.base import Base


class MaintenanceRequestModel(Base):
    """
    The partial unique index `uq_open_maintenance_per_asset` (asset_id WHERE
    status IN the "open" set — see migration 0004) guarantees at the DB
    level that an asset can never have two simultaneously-open maintenance
    requests, the same pattern used for `uq_active_allocation_per_asset` in
    Phase 3. Declared via raw SQL in the migration for the same reason:
    SQLAlchemy's declarative Constraint API can't express a partial index.
    """

    __tablename__ = "maintenance_requests"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    raised_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    issue_description: Mapped[str] = mapped_column(String(2000), nullable=False)
    priority: Mapped[MaintenancePriority] = mapped_column(
        SAEnum(MaintenancePriority, name="maintenance_priority", native_enum=True), nullable=False
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        SAEnum(MaintenanceStatus, name="maintenance_status", native_enum=True),
        nullable=False,
        default=MaintenanceStatus.PENDING,
        index=True,
    )
    photo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    approved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    assigned_technician_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assigned_technician_contact: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)
