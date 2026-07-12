from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.asset import AssetStatus
from src.infrastructure.database.models.base import Base


class AssetStateTransitionModel(Base):
    """
    Append-only audit trail of every status change on an asset. Never
    updated or deleted — this is what backs the 'per-asset history' view
    on Screen 4 and gives Reports & Analytics something to compute
    maintenance-frequency / utilization trends from later.
    """

    __tablename__ = "asset_state_transitions"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_state: Mapped[AssetStatus] = mapped_column(SAEnum(AssetStatus, name="asset_status", native_enum=True), nullable=False)
    to_state: Mapped[AssetStatus] = mapped_column(SAEnum(AssetStatus, name="asset_status", native_enum=True), nullable=False)
    triggered_by_user_id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
