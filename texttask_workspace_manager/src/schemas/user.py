# src/schemas/user.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    username: Optional[str] = Field(None, min_length=3, max_length=50, example="cooluser")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Plain-text password (will be hashed)")


class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted: bool = False
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # allows .from_orm() / model_validate(obj)


class UserInDB(UserRead):
    password_hash: str