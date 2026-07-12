from __future__ import annotations

import uuid

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.application.services.auth_service import AuthService
from src.domain.entities.user import Role, User, UserStatus
from src.domain.exceptions.domain_exceptions import EntityNotFoundError, InsufficientPermissionError


class EmployeeDirectoryService:
    """
    Backs Screen 3 / Tab C: Employee Directory.
    Listing/searching is available to Admins (full org-wide view). Role
    promotion is delegated to AuthService.promote_user, which remains the
    single source of truth for that operation.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow
        self._auth_service = AuthService(uow)

    async def list_employees(
        self, *, acting_user: User, role: Role | None = None, department_id: uuid.UUID | None = None, search: str | None = None
    ) -> list[User]:
        if not acting_user.can_manage_organization():
            raise InsufficientPermissionError(required_roles=["ADMIN"])

        async with self._uow as uow:
            return await uow.users.list_all(role=role, department_id=department_id, search=search)

    async def set_employee_status(self, *, acting_user: User, target_user_id: uuid.UUID, status: UserStatus) -> User:
        if not acting_user.can_manage_organization():
            raise InsufficientPermissionError(required_roles=["ADMIN"])

        async with self._uow as uow:
            target = await uow.users.get_by_id_for_update(target_user_id)
            if target is None:
                raise EntityNotFoundError("User", str(target_user_id))
            target.status = status
            updated = await uow.users.update(target)
            await uow.commit()
            return updated

    async def promote_employee(self, *, acting_user: User, target_user_id: uuid.UUID, new_role: Role) -> User:
        """Thin pass-through — kept here so the router only ever talks to directory concerns."""
        return await self._auth_service.promote_user(
            acting_admin=acting_user, target_user_id=target_user_id, new_role=new_role
        )
