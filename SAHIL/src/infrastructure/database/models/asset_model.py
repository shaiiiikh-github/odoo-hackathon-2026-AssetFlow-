from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, Enum as SAEnum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.domain.entities.asset import AssetCondition, AssetStatus
from src.infrastructure.database.models.base import Base


class AssetModel(Base):
    __tablename__ = "assets"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    asset_tag: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    serial_number: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    category_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("asset_categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[AssetStatus] = mapped_column(
        SAEnum(AssetStatus, name="asset_status", native_enum=True), nullable=False, default=AssetStatus.AVAILABLE, index=True
    )
    condition: Mapped[AssetCondition] = mapped_column(
        SAEnum(AssetCondition, name="asset_condition", native_enum=True), nullable=False, default=AssetCondition.GOOD
    )
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    is_bookable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    acquisition_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    acquisition_cost: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    photo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    document_urls: Mapped[list[str]] = mapped_column(ARRAY(String(1024)), nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)
