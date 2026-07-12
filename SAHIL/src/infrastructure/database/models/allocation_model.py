from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.allocation import AllocationStatus
from src.infrastructure.database.models.base import Base


class AllocationModel(Base):
    """
    One row per custody period. The partial unique index
    `uq_active_allocation_per_asset` (asset_id WHERE status='ACTIVE'),
    created in migration 0003, is the load-bearing guarantee that at most
    one ACTIVE row can ever exist per asset_id — it is NOT declared as a
    SQLAlchemy `UniqueConstraint` here because SQLAlchemy's declarative
    Column/Constraint API can't express a partial (WHERE-qualified) index;
    it's created directly via op.execute() in the migration instead.
    """

    __tablename__ = "allocations"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    holder_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    holder_department_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    allocated_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

    status: Mapped[AllocationStatus] = mapped_column(
        SAEnum(AllocationStatus, name="allocation_status", native_enum=True),
        nullable=False,
        default=AllocationStatus.ACTIVE,
        index=True,
    )
    expected_return_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    allocated_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    returned_at: Mapped[datetime | None] = mapped_column(nullable=True)
    return_condition_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        # A holder must be a person OR a department, never neither/both left
        # ambiguous by the app layer — cheap defense-in-depth at the DB level.
        CheckConstraint(
            "holder_user_id IS NOT NULL OR holder_department_id IS NOT NULL",
            name="ck_allocations_has_holder",
        ),
    )
