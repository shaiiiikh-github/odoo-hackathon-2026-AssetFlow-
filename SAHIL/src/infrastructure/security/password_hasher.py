from __future__ import annotations

from passlib.context import CryptContext

from src.core.config import get_settings

settings = get_settings()

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)


class PasswordHasher:
    """Thin wrapper so services never import passlib directly (keeps infra swappable)."""

    @staticmethod
    def hash(plain_password: str) -> str:
        return _pwd_context.hash(plain_password)

    @staticmethod
    def verify(plain_password: str, password_hash: str) -> bool:
        return _pwd_context.verify(plain_password, password_hash)
