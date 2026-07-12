from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.allocation import TransferStatus
from src.infrastructure.database.models.base import Base


class TransferRequestModel(Base):
    __tablename__ = "transfer_requests"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_allocation_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("allocations.id", ondelete="CASCADE"), nullable=False
    )
    requested_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    requested_for_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    requested_for_department_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )

    status: Mapped[TransferStatus] = mapped_column(
        SAEnum(TransferStatus, name="transfer_status", native_enum=True),
        nullable=False,
        default=TransferStatus.REQUESTED,
        index=True,
    )
    requested_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    resolved_by_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "requested_for_user_id IS NOT NULL OR requested_for_department_id IS NOT NULL",
            name="ck_transfer_requests_has_target",
        ),
    )
