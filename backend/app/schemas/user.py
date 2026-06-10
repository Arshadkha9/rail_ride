from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


class UserBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(BaseSchema):
    id: int
    full_name: str
    email: Optional[str] = None
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime


class ProfileResponse(UserResponse):
    wallet_balance: Optional[float] = None
    total_rides: int = 0
    total_trips: int = 0
