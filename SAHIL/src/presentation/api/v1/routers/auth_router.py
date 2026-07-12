from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from src.application.services.auth_service import AuthService
from src.domain.entities.user import Role, User
from src.presentation.api.v1.schemas.auth_schemas import (
    LoginRequest,
    PromoteRoleRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from src.presentation.dependencies import get_auth_service
from src.presentation.middleware.auth_middleware import get_current_user, require_admin

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, auth_service: AuthService = Depends(get_auth_service)) -> UserResponse:
    """Creates an EMPLOYEE account only. No role field exists on this request by design."""
    user = await auth_service.signup(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        department_id=payload.department_id,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    _, tokens = await auth_service.login(payload.email, payload.password)
    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    tokens = await auth_service.refresh_access_token(payload.refresh_token)
    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.post("/users/{user_id}/promote", response_model=UserResponse)
async def promote_user(
    user_id: uuid.UUID,
    payload: PromoteRoleRequest,
    acting_admin: User = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Admin-only. This is the single endpoint in the system capable of turning an
    EMPLOYEE into a DEPARTMENT_HEAD or ASSET_MANAGER — per the spec, 'this is
    the only place roles are assigned.'
    """
    updated = await auth_service.promote_user(
        acting_admin=acting_admin, target_user_id=user_id, new_role=payload.new_role
    )
    return UserResponse.model_validate(updated)
