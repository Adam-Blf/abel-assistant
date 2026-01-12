"""
===============================================================================
AUTH RESPONSES - Authentication Response Schemas
===============================================================================
A.B.E.L. Project - Pydantic models for auth responses
===============================================================================
"""

from typing import Optional

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """User information response."""

    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: Optional[str] = Field(None, description="User display name")
    created_at: Optional[str] = Field(None, description="Account creation date")


class TokensResponse(BaseModel):
    """Authentication tokens response."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    expires_in: int = Field(..., description="Token expiry in seconds")
    token_type: str = Field(default="bearer", description="Token type")


class AuthResponse(BaseModel):
    """Full authentication response with user and tokens."""

    user: UserResponse
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")
