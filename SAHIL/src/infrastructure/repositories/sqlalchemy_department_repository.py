from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_department_repository import IDepartmentRepository
from src.domain.entities.department import Department, DepartmentStatus
from src.infrastructure.database.models.department_model import DepartmentModel
from src.infrastructure.database.models.user_model import UserModel


class SqlAlchemyDepartmentRepository(IDepartmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_entity(model: DepartmentModel) -> Department:
        return Department(
            id=model.id,
            name=model.name,
            status=model.status,
            parent_department_id=model.parent_department_id,
            head_user_id=model.head_user_id,
            created_at=model.created_at,
        )

    async def add(self, department: Department) -> Department:
        model = DepartmentModel(
            id=department.id,
            name=department.name,
            status=department.status,
            parent_department_id=department.parent_department_id,
            head_user_id=department.head_user_id,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, department_id: UUID) -> Department | None:
        model = await self._session.get(DepartmentModel, department_id)
        return self._to_entity(model) if model else None

    async def get_by_name(self, name: str) -> Department | None:
        stmt = select(DepartmentModel).where(DepartmentModel.name == name)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, *, status: str | None = None) -> list[Department]:
        stmt = select(DepartmentModel)
        if status is not None:
            stmt = stmt.where(DepartmentModel.status == status)
        result = await self._session.execute(stmt.order_by(DepartmentModel.name))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, department: Department) -> Department:
        model = await self._session.get(DepartmentModel, department.id)
        if model is None:
            raise ValueError(f"Department {department.id} does not exist and cannot be updated.")
        model.name = department.name
        model.status = department.status
        model.parent_department_id = department.parent_department_id
        model.head_user_id = department.head_user_id
        await self._session.flush()
        return self._to_entity(model)

    async def has_active_children_or_employees(self, department_id: UUID) -> bool:
        child_stmt = select(DepartmentModel.id).where(
            DepartmentModel.parent_department_id == department_id,
            DepartmentModel.status == DepartmentStatus.ACTIVE,
        )
        employee_stmt = select(UserModel.id).where(UserModel.department_id == department_id)

        child_result = await self._session.execute(child_stmt.limit(1))
        if child_result.first() is not None:
            return True

        employee_result = await self._session.execute(employee_stmt.limit(1))
        return employee_result.first() is not None

    async def get_ancestor_ids(self, department_id: UUID) -> set[UUID]:
        ancestors: set[UUID] = set()
        current_id: UUID | None = department_id
        # Bounded walk (max 50 hops) guards against any pre-existing bad data forming a loop.
        for _ in range(50):
            model = await self._session.get(DepartmentModel, current_id)
            if model is None or model.parent_department_id is None:
                break
            ancestors.add(model.parent_department_id)
            current_id = model.parent_department_id
        return ancestors
