from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class Role(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    ASSET_MANAGER = "ASSET_MANAGER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass
class User:
    """
    Pure domain entity — no ORM/framework dependency.
    Business invariants about a User live here, not in the ORM model or the router.
    """

    id: UUID
    email: str
    password_hash: str
    full_name: str
    role: Role
    status: UserStatus
    department_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE

    def can_manage_organization(self) -> bool:
        """Only Admins can touch master data (departments, categories, role assignment)."""
        return self.role == Role.ADMIN

    def can_manage_assets(self) -> bool:
        return self.role in (Role.ADMIN, Role.ASSET_MANAGER)

    def promote(self, new_role: Role) -> None:
        """
        Domain-level guard: a user can never promote themselves to ADMIN via this path,
        and EMPLOYEE is the only role assignable at signup — enforced in the service layer
        by *who* is allowed to call this, not by this method alone.
        """
        if new_role == Role.EMPLOYEE:
            raise ValueError("Cannot 'promote' a user to EMPLOYEE; that is the default role.")
        self.role = new_role
