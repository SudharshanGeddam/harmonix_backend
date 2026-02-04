"""
Pydantic schemas for authentication endpoints.

Defines request and response models for signup and login operations.
"""

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request model for user signup."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ..., min_length=6, description="User password (minimum 6 characters)"
    )


class LoginRequest(BaseModel):
    """Request model for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Response model containing user information."""

    id: str = Field(..., description="User unique identifier")
    email: str = Field(..., description="User email address")


class SignupResponse(BaseModel):
    """Response model for signup endpoint."""

    user: UserResponse = Field(..., description="Created user information")
    message: str = Field(default="User created successfully")


class LoginResponse(BaseModel):
    """Response model for login endpoint."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    user: UserResponse = Field(..., description="Authenticated user information")
    token_type: str = Field(default="bearer", description="Token type")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")
