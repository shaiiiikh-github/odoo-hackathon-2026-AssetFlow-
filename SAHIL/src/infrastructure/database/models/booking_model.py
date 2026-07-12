from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import TSTZRANGE, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.booking import BookingStatus
from src.infrastructure.database.models.base import Base


class BookingModel(Base):
    """
    `time_range` is a STORED GENERATED column (see migration 0003) computed
    from start_time/end_time as `tstzrange(start_time, end_time, '[)')`. It
    exists purely so Postgres has something to index with GIST and enforce
    the `EXCLUDE USING gist (asset_id WITH =, time_range WITH &&)` constraint
    against — that constraint, not this ORM class, is what actually makes
    overlapping bookings for the same resource impossible to commit. We map
    it here read-only (never set it from Python) so it's still visible on
    a loaded row without SQLAlchemy trying to manage it.
    """

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    booked_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_range = mapped_column(TSTZRANGE, nullable=True, insert_default=None)  # DB-generated; app never writes this

    status: Mapped[BookingStatus] = mapped_column(
        SAEnum(BookingStatus, name="booking_status", native_enum=True),
        nullable=False,
        default=BookingStatus.UPCOMING,
        index=True,
    )
    purpose: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_bookings_end_after_start"),
    )
