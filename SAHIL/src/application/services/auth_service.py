from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.application.interfaces.i_unit_of_work import IUnitOfWork
from src.domain.entities.user import Role, User, UserStatus
from src.domain.exceptions.domain_exceptions import (
    DuplicateEmailError,
    InactiveAccountError,
    InsufficientPermissionError,
    InvalidCredentialsError,
    InvalidRolePromotionError,
)
from src.infrastructure.security.jwt_handler import JwtHandler, TokenType
from src.infrastructure.security.password_hasher import PasswordHasher


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    """
    Owns every rule about who is allowed to become what.

    Hard rule enforced here (not just at the API layer): signup ALWAYS produces
    an EMPLOYEE. There is no code path in this service where a caller-supplied
    role reaches user creation during signup — role is not even a parameter of
    `signup()`. Promotion is a distinct, explicitly Admin-gated operation.
    """

    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def signup(self, email: str, password: str, full_name: str, department_id: uuid.UUID | None) -> User:
        normalized_email = email.strip().lower()

        async with self._uow as uow:
            existing = await uow.users.get_by_email(normalized_email)
            if existing is not None:
                raise DuplicateEmailError(normalized_email)

            user = User(
                id=uuid.uuid4(),
                email=normalized_email,
                password_hash=PasswordHasher.hash(password),
                full_name=full_name.strip(),
                role=Role.EMPLOYEE,          # <-- hardcoded, not caller-controlled
                status=UserStatus.ACTIVE,
                department_id=department_id,
            )
            created = await uow.users.add(user)
            await uow.commit()
            return created

    async def login(self, email: str, password: str) -> tuple[User, TokenPair]:
        async with self._uow as uow:
            user = await uow.users.get_by_email(email.strip().lower())

        if user is None or not PasswordHasher.verify(password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active():
            raise InactiveAccountError()

        tokens = self._issue_tokens(user)
        return user, tokens

    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        payload = JwtHandler.decode(refresh_token, expected_type=TokenType.REFRESH)
        user_id = uuid.UUID(payload["sub"])

        async with self._uow as uow:
            user = await uow.users.get_by_id(user_id)

        if user is None or not user.is_active():
            raise InactiveAccountError()

        return self._issue_tokens(user)

    async def promote_user(self, *, acting_admin: User, target_user_id: uuid.UUID, new_role: Role) -> User:
        """
        The ONLY code path in the entire system that assigns DEPARTMENT_HEAD or
        ASSET_MANAGER. Guarded twice: (1) caller role check here as defense in
        depth even though the router already enforces RBAC, (2) row-level lock
        on the target user to prevent two concurrent promotion requests from
        interleaving and leaving the record in an inconsistent audit trail.
        """
        if not acting_admin.can_manage_organization():
            raise InsufficientPermissionError(required_roles=[Role.ADMIN.value])

        if new_role not in (Role.DEPARTMENT_HEAD, Role.ASSET_MANAGER, Role.ADMIN):
            raise InvalidRolePromotionError(f"'{new_role}' is not a valid promotion target.")

        if target_user_id == acting_admin.id and new_role != Role.ADMIN:
            # Admins demoting themselves is a deliberate separate flow (not covered here)
            # to avoid an Admin accidentally locking themselves out mid-request.
            raise InvalidRolePromotionError("Use the dedicated self-demotion flow to change your own role.")

        async with self._uow as uow:
            target = await uow.users.get_by_id_for_update(target_user_id)
            if target is None:
                raise InvalidRolePromotionError(f"Target user {target_user_id} does not exist.")

            target.promote(new_role)
            updated = await uow.users.update(target)
            await uow.commit()
            return updated

    @staticmethod
    def _issue_tokens(user: User) -> TokenPair:
        access = JwtHandler.create_access_token(
            user_id=user.id,
            role=user.role.value,
            department_id=str(user.department_id) if user.department_id else None,
        )
        refresh = JwtHandler.create_refresh_token(user_id=user.id)
        return TokenPair(access_token=access, refresh_token=refresh)
