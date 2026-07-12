from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.interfaces.repositories.i_user_repository import IUserRepository
from src.domain.entities.user import Role, User, UserStatus
from src.infrastructure.database.models.user_model import UserModel


class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # --- mapping helpers -------------------------------------------------
    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            role=model.role,
            status=model.status,
            department_id=model.department_id,
            created_at=model.created_at,
        )

    # --- interface implementation ----------------------------------------
    async def add(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            department_id=user.department_id,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    async def get_by_id_for_update(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id).with_for_update()
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_by_department(self, department_id: UUID) -> list[User]:
        stmt = select(UserModel).where(UserModel.department_id == department_id)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_all(
        self, *, role: Role | None = None, department_id: UUID | None = None, search: str | None = None
    ) -> list[User]:
        stmt = select(UserModel)
        if role is not None:
            stmt = stmt.where(UserModel.role == role)
        if department_id is not None:
            stmt = stmt.where(UserModel.department_id == department_id)
        if search:
            like = f"%{search.lower()}%"
            stmt = stmt.where(UserModel.full_name.ilike(like) | UserModel.email.ilike(like))
        result = await self._session.execute(stmt.order_by(UserModel.full_name))
        return [self._to_entity(m) for m in result.scalars().all()]

    async def update(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise ValueError(f"User {user.id} does not exist and cannot be updated.")
        model.full_name = user.full_name
        model.role = user.role
        model.status = user.status
        model.department_id = user.department_id
        model.password_hash = user.password_hash
        await self._session.flush()
        return self._to_entity(model)
