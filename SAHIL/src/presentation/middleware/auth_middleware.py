from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.user import Role, User
from src.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.security.jwt_handler import InvalidTokenError, JwtHandler, TokenType

_bearer_scheme = HTTPBearer(auto_error=False)


def get_unit_of_work() -> IUnitOfWork:
    """Composition-root factory — swap this single line to change persistence impl app-wide."""
    return SqlAlchemyUnitOfWork()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> User:
    """
    Validates the JWT, then re-fetches the user from the DB (session validation)
    rather than trusting the token payload alone — this is what catches a user
    who was deactivated by an Admin AFTER their token was issued.
    """
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")

    try:
        payload = JwtHandler.decode(credentials.credentials, expected_type=TokenType.ACCESS)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}") from exc

    user_id = uuid.UUID(payload["sub"])

    async with uow as u:
        user = await u.users.get_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    if not user.is_active():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")

    return user


def require_roles(*allowed_roles: Role) -> Callable[[User], User]:
    """
    RBAC guard factory — usage on a route:

        @router.post("/departments", dependencies=[Depends(require_roles(Role.ADMIN))])

    or, if the handler also needs the user object:

        async def create_department(acting_user: User = Depends(require_roles(Role.ADMIN))): ...

    Kept as a dependency (not a decorator) so it composes naturally with FastAPI's
    DI graph and is trivially unit-testable in isolation.
    """

    async def _guard(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {', '.join(r.value for r in allowed_roles)}.",
            )
        return current_user

    return _guard


# Common shorthand guards used across routers
require_admin = require_roles(Role.ADMIN)
require_asset_manager_or_admin = require_roles(Role.ADMIN, Role.ASSET_MANAGER)
require_department_head_or_above = require_roles(Role.ADMIN, Role.ASSET_MANAGER, Role.DEPARTMENT_HEAD)
require_any_authenticated = get_current_user
