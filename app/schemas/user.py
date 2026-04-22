from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Schema for user registration request
class UserCreate(BaseModel):
    username: str = Field(
        description="Username for registration",
        examples=["uki_dev"],
    )
    email: EmailStr = Field(
        description="Email address for registration",
        examples=["uki@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password for login, minimum 8 characters",
        examples=["mysecret123"],
    )
    bio: str | None = Field(
        default=None,
        max_length=255,
        description="User bio, optional",
        examples=["Bio of the user, can be null"],
    )


# Schema for user registration response
class UserResponse(BaseModel):
    id: int = Field(description="User ID", examples=[1])
    username: str = Field(description="Username", examples=["uki_dev"])
    email: EmailStr = Field(description="Email address", examples=["uki@example.com"])
    role: str = Field(description="User role", examples=["user"])
    bio: str | None = Field(
        default=None,
        description="User bio, optional",
        examples=["Bio of the user, can be null"],
    )
    created_at: datetime = Field(
        description="Account creation time",
        examples=["2026-04-21T23:00:00"],
    )
    is_active: bool = Field(description="Account activation status", examples=[True])

    model_config = ConfigDict(
        from_attributes=True
    )  # Enable ORM mode for SQLAlchemy models, needed for converting dictionary data to pydantic models.


# Schema for user login request
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for JWT token response
class TokenResponse(BaseModel):
    access_token: str = Field(
        description="JWT access token issued after successful login",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example.token"],
    )
    token_type: str = Field(
        description="Token type, usually bearer",
        examples=["bearer"],
    )
