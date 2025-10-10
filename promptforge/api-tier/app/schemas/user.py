"""
User schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.user import UserRole


# Authentication schemas
class UserLogin(BaseModel):
    """User login request"""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request"""

    refresh_token: str


# User schemas
class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.DEVELOPER


class UserCreate(UserBase):
    """User creation schema"""

    password: str = Field(..., min_length=8)
    organization_id: UUID


class UserUpdate(BaseModel):
    """User update schema"""

    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    is_active: bool
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
