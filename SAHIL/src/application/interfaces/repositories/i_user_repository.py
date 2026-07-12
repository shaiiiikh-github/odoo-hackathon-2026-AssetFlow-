from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.entities.user import Role, User


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> User:
        ...

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def list_by_department(self, department_id: UUID) -> list[User]:
        ...

    @abstractmethod
    async def list_all(
        self, *, role: Role | None = None, department_id: UUID | None = None, search: str | None = None
    ) -> list[User]:
        ...

    @abstractmethod
    async def update(self, user: User) -> User:
        ...

    @abstractmethod
    async def get_by_id_for_update(self, user_id: UUID) -> User | None:
        """
        Fetch with SELECT ... FOR UPDATE — used during role promotion to prevent
        two concurrent promotion requests on the same user from racing.
        """
        ...
