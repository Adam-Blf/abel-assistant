"""
===============================================================================
AUTH.PY - Authentication API Endpoints
===============================================================================
A.B.E.L. Project - User authentication endpoints
Rate limited and validated
===============================================================================
"""

import logging

from fastapi import APIRouter, Depends, Request

from app.core.security.auth import get_current_user
from app.core.security.rate_limiter import limiter
from app.schemas.requests.auth import (
    LoginRequest,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from app.schemas.responses.auth import AuthResponse, MessageResponse, UserResponse
from app.services.supabase.auth import AuthUser, get_auth_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: RegisterRequest,
) -> AuthResponse:
    """
    Register a new user account.

    Rate limited to 5 requests per minute.

    Args:
        request: FastAPI request (for rate limiting)
        data: Registration data (email, password, name)

    Returns:
        AuthResponse with user info and tokens
    """
    logger.info(f"Registration attempt for: {data.email}")

    auth_service = get_auth_service()
    result = await auth_service.register(
        email=data.email,
        password=data.password,
        name=data.name,
    )

    logger.info(f"User registered: {result.user.id}")

    return AuthResponse(
        user=UserResponse(
            id=result.user.id,
            email=result.user.email,
            name=result.user.name,
            created_at=result.user.created_at,
        ),
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
        expires_in=result.tokens.expires_in,
        token_type=result.tokens.token_type,
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    data: LoginRequest,
) -> AuthResponse:
    """
    Login with email and password.

    Rate limited to 10 requests per minute.

    Args:
        request: FastAPI request (for rate limiting)
        data: Login credentials (email, password)

    Returns:
        AuthResponse with user info and tokens
    """
    logger.info(f"Login attempt for: {data.email}")

    auth_service = get_auth_service()
    result = await auth_service.login(
        email=data.email,
        password=data.password,
    )

    logger.info(f"User logged in: {result.user.id}")

    return AuthResponse(
        user=UserResponse(
            id=result.user.id,
            email=result.user.email,
            name=result.user.name,
            created_at=result.user.created_at,
        ),
        access_token=result.tokens.access_token,
        refresh_token=result.tokens.refresh_token,
        expires_in=result.tokens.expires_in,
        token_type=result.tokens.token_type,
    )


@router.post("/refresh", response_model=AuthResponse)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    data: RefreshTokenRequest,
) -> dict:
    """
    Refresh access token using refresh token.

    Rate limited to 30 requests per minute.

    Args:
        request: FastAPI request (for rate limiting)
        data: Refresh token

    Returns:
        New tokens
    """
    auth_service = get_auth_service()
    tokens = await auth_service.refresh_token(data.refresh_token)

    return {
        "access_token": tokens.access_token,
        "refresh_token": tokens.refresh_token,
        "expires_in": tokens.expires_in,
        "token_type": tokens.token_type,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: AuthUser = Depends(get_current_user),
) -> UserResponse:
    """
    Get current authenticated user information.

    Requires valid Bearer token.

    Returns:
        UserResponse with user info
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        created_at=current_user.created_at,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: AuthUser = Depends(get_current_user),
) -> MessageResponse:
    """
    Logout current user (invalidate session).

    Returns:
        Success message
    """
    # Get token from header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else ""

    auth_service = get_auth_service()
    await auth_service.logout(token)

    logger.info(f"User logged out: {current_user.id}")

    return MessageResponse(
        message="Successfully logged out",
        success=True,
    )


@router.post("/password-reset", response_model=MessageResponse)
@limiter.limit("3/minute")
async def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
) -> MessageResponse:
    """
    Request password reset email.

    Rate limited to 3 requests per minute.

    Args:
        request: FastAPI request (for rate limiting)
        data: Email address

    Returns:
        Success message (always returns success for security)
    """
    auth_service = get_auth_service()
    await auth_service.request_password_reset(data.email)

    # Always return success (don't reveal if email exists)
    return MessageResponse(
        message="If an account exists with this email, a reset link has been sent.",
        success=True,
    )
