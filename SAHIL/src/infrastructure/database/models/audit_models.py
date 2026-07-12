from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Date, Enum as SAEnum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.audit import AuditCycleStatus, AuditFindingStatus
from src.infrastructure.database.models.base import Base


class AuditCycleModel(Base):
    __tablename__ = "audit_cycles"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[AuditCycleStatus] = mapped_column(
        SAEnum(AuditCycleStatus, name="audit_cycle_status", native_enum=True),
        nullable=False,
        default=AuditCycleStatus.OPEN,
        index=True,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    closed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AuditAssignmentModel(Base):
    __tablename__ = "audit_assignments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    auditor_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("cycle_id", "auditor_user_id", name="uq_audit_assignment_cycle_auditor"),)


class AuditFindingModel(Base):
    """
    `uq_audit_finding_cycle_asset` makes (cycle_id, asset_id) a natural key:
    an auditor's second submission for the same asset in the same cycle
    UPDATEs the existing row (see SqlAlchemyAuditRepository.upsert_finding)
    rather than creating a duplicate. This is what lets an auditor correct
    a mis-click without producing conflicting rows for the discrepancy
    report to reconcile.
    """

    __tablename__ = "audit_findings"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("audit_cycles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    asset_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    marked_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    status: Mapped[AuditFindingStatus] = mapped_column(
        SAEnum(AuditFindingStatus, name="audit_finding_status", native_enum=True),
        nullable=False,
        default=AuditFindingStatus.PENDING,
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    marked_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (UniqueConstraint("cycle_id", "asset_id", name="uq_audit_finding_cycle_asset"),)
