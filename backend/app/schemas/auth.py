from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    company_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=1,
        max_length=72,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    organization_id: UUID
    role: str


class RegisterResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str
    token_type: str = "bearer"