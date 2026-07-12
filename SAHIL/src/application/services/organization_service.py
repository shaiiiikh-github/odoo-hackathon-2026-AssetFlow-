from __future__ import annotations

import uuid

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.asset_category import AssetCategory
from src.domain.entities.department import Department, DepartmentStatus
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import (
    DepartmentHierarchyCycleError,
    DepartmentInUseError,
    DuplicateCategoryNameError,
    EntityNotFoundError,
    InsufficientPermissionError,
)


def _require_admin(user: User) -> None:
    if not user.can_manage_organization():
        raise InsufficientPermissionError(required_roles=["ADMIN"])


class OrganizationService:
    """
    Master-data service for Departments and Asset Categories.
    Every write path re-checks `acting_user.can_manage_organization()` as a
    defense-in-depth measure even though the router-level RBAC dependency
    already blocks non-Admins before the request body is even parsed.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    # ---------------------------------------------------------------- Departments
    async def create_department(
        self, *, acting_user: User, name: str, parent_department_id: uuid.UUID | None, head_user_id: uuid.UUID | None
    ) -> Department:
        _require_admin(acting_user)

        async with self._uow as uow:
            if parent_department_id is not None:
                parent = await uow.departments.get_by_id(parent_department_id)
                if parent is None:
                    raise EntityNotFoundError("Department", str(parent_department_id))

            if head_user_id is not None:
                head = await uow.users.get_by_id(head_user_id)
                if head is None:
                    raise EntityNotFoundError("User", str(head_user_id))

            department = Department(
                id=uuid.uuid4(),
                name=name.strip(),
                status=DepartmentStatus.ACTIVE,
                parent_department_id=parent_department_id,
                head_user_id=head_user_id,
            )
            created = await uow.departments.add(department)
            await uow.commit()
            return created

    async def update_department(
        self,
        *,
        acting_user: User,
        department_id: uuid.UUID,
        name: str | None,
        parent_department_id: uuid.UUID | None,
        head_user_id: uuid.UUID | None,
        status: DepartmentStatus | None,
    ) -> Department:
        _require_admin(acting_user)

        async with self._uow as uow:
            department = await uow.departments.get_by_id(department_id)
            if department is None:
                raise EntityNotFoundError("Department", str(department_id))

            if parent_department_id is not None:
                if department.would_create_cycle(parent_department_id):
                    raise DepartmentHierarchyCycleError()
                # Full-chain check: candidate parent must not be a descendant of this dept.
                ancestors_of_candidate = await uow.departments.get_ancestor_ids(parent_department_id)
                if department_id in ancestors_of_candidate or parent_department_id == department_id:
                    raise DepartmentHierarchyCycleError()
                department.parent_department_id = parent_department_id

            if status == DepartmentStatus.INACTIVE and department.status == DepartmentStatus.ACTIVE:
                in_use = await uow.departments.has_active_children_or_employees(department_id)
                if in_use:
                    raise DepartmentInUseError(str(department_id))
                department.deactivate()
            elif status is not None:
                department.status = status

            if name is not None:
                department.name = name.strip()
            if head_user_id is not None:
                department.assign_head(head_user_id)

            updated = await uow.departments.update(department)
            await uow.commit()
            return updated

    async def list_departments(self, *, status: DepartmentStatus | None = None) -> list[Department]:
        async with self._uow as uow:
            return await uow.departments.list_all(status=status.value if status else None)

    async def get_department(self, department_id: uuid.UUID) -> Department:
        async with self._uow as uow:
            department = await uow.departments.get_by_id(department_id)
        if department is None:
            raise EntityNotFoundError("Department", str(department_id))
        return department

    # ---------------------------------------------------------------- Asset Categories
    async def create_category(
        self, *, acting_user: User, name: str, custom_fields_schema: dict
    ) -> AssetCategory:
        _require_admin(acting_user)

        async with self._uow as uow:
            existing = await uow.categories.get_by_name(name.strip())
            if existing is not None:
                raise DuplicateCategoryNameError(name)

            category = AssetCategory(id=uuid.uuid4(), name=name.strip(), custom_fields_schema=custom_fields_schema)
            created = await uow.categories.add(category)
            await uow.commit()
            return created

    async def update_category(
        self, *, acting_user: User, category_id: uuid.UUID, name: str | None, custom_fields_schema: dict | None
    ) -> AssetCategory:
        _require_admin(acting_user)

        async with self._uow as uow:
            category = await uow.categories.get_by_id(category_id)
            if category is None:
                raise EntityNotFoundError("AssetCategory", str(category_id))

            if name is not None and name.strip() != category.name:
                clash = await uow.categories.get_by_name(name.strip())
                if clash is not None:
                    raise DuplicateCategoryNameError(name)
                category.name = name.strip()

            if custom_fields_schema is not None:
                category.custom_fields_schema = custom_fields_schema

            updated = await uow.categories.update(category)
            await uow.commit()
            return updated

    async def list_categories(self) -> list[AssetCategory]:
        async with self._uow as uow:
            return await uow.categories.list_all()
