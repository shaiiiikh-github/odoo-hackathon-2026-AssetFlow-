from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.domain.entities.user import Role, UserStatus


class SignupRequest(BaseModel):
    """
    Deliberately has NO 'role' field. This is the enforcement mechanism at the
    schema level: even a malicious client cannot smuggle a role into signup
    because there is nowhere in this model to put it.
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    department_id: uuid.UUID | None = None

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: Role
    status: UserStatus
    department_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class PromoteRoleRequest(BaseModel):
    new_role: Role

    @field_validator("new_role")
    @classmethod
    def must_be_promotable(cls, v: Role) -> Role:
        if v == Role.EMPLOYEE:
            raise ValueError("Cannot 'promote' to EMPLOYEE — that is the default signup role.")
        return v
