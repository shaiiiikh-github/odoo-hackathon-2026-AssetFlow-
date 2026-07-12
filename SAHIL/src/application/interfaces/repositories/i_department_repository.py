from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.department import Department


class IDepartmentRepository(ABC):
    @abstractmethod
    async def add(self, department: Department) -> Department:
        ...

    @abstractmethod
    async def get_by_id(self, department_id: UUID) -> Department | None:
        ...

    @abstractmethod
    async def get_by_name(self, name: str) -> Department | None:
        ...

    @abstractmethod
    async def list_all(self, *, status: str | None = None) -> list[Department]:
        ...

    @abstractmethod
    async def update(self, department: Department) -> Department:
        ...

    @abstractmethod
    async def has_active_children_or_employees(self, department_id: UUID) -> bool:
        """Used to block deactivation of a department still in use."""
        ...

    @abstractmethod
    async def get_ancestor_ids(self, department_id: UUID) -> set[UUID]:
        """
        Walks parent_department_id chain upward. Used to detect cycles before
        assigning a new parent (candidate parent must not be a descendant of self).
        """
        ...
