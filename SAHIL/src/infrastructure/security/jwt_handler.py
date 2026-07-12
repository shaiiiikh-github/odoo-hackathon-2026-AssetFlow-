from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

import jwt
from jwt import PyJWTError

from src.core.config import get_settings

settings = get_settings()


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class InvalidTokenError(Exception):
    pass


class JwtHandler:
    """
    Encodes/decodes access & refresh tokens. Role and status are embedded in the
    access token payload so the RBAC middleware can authorize without a DB hit
    on every request; session_validation still re-checks against the DB for
    high-sensitivity operations (see AuthMiddleware.require_fresh_session).
    """

    @staticmethod
    def create_access_token(user_id: UUID, role: str, department_id: str | None) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "role": role,
            "department_id": department_id,
            "type": TokenType.ACCESS.value,
            "iat": now,
            "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": TokenType.REFRESH.value,
            "iat": now,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def decode(token: str, expected_type: TokenType) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except PyJWTError as exc:
            raise InvalidTokenError(str(exc)) from exc

        if payload.get("type") != expected_type.value:
            raise InvalidTokenError(f"Expected a {expected_type.value} token.")
        return payload
