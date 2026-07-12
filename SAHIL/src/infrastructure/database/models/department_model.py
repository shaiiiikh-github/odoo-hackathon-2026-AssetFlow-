from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.domain.entities.department import DepartmentStatus
from src.infrastructure.database.models.base import Base


class DepartmentModel(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    parent_department_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("departments.id", ondelete="SET NULL"), nullable=True
    )
    # Nullable FK to users; the reverse (users.department_id) is enforced separately.
    # No FK constraint here to sidestep a circular FK dependency at table-creation time —
    # referential integrity for head_user_id is enforced at the service layer.
    head_user_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    status: Mapped[DepartmentStatus] = mapped_column(
        SAEnum(DepartmentStatus, name="department_status", native_enum=True),
        nullable=False,
        default=DepartmentStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)

    parent: Mapped["DepartmentModel | None"] = relationship(
        "DepartmentModel", remote_side=[id], backref="children"
    )
    employees: Mapped[list["UserModel"]] = relationship(
        "UserModel", back_populates="department", foreign_keys="UserModel.department_id"
    )
