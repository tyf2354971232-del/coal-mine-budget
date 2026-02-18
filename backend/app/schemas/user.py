"""User schemas."""
from pydantic import BaseModel
from typing import Optional
from app.schemas.types import FormattedDatetime


class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: str = "viewer"
    department: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    department: Optional[str]
    is_active: bool
    created_at: FormattedDatetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
