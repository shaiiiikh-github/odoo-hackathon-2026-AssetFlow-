from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from app.infrastructure.database.models import UserRole

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    department_id: Optional[UUID] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    department_id: Optional[UUID] = None
    is_active: Optional[bool] = None

# Properties to return to client
class UserResponse(UserBase):
    id: UUID
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True # Allows Pydantic to read ORM models