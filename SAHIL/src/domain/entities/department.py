from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID


class DepartmentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass
class Department:
    """
    Supports optional self-referencing parent for organizational hierarchy
    (e.g. 'Engineering' -> parent 'Technology Division').
    """

    id: UUID
    name: str
    status: DepartmentStatus
    parent_department_id: UUID | None = None
    head_user_id: UUID | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def deactivate(self) -> None:
        self.status = DepartmentStatus.INACTIVE

    def assign_head(self, user_id: UUID) -> None:
        self.head_user_id = user_id

    def would_create_cycle(self, candidate_parent_id: UUID) -> bool:
        """
        Guard against a department being set as its own ancestor.
        Direct self-parent check; full ancestry-chain check happens in the
        service layer where the repository can walk the tree.
        """
        return candidate_parent_id == self.id
