"""
===============================================================================
AUTH.PY - JWT Authentication & Authorization
===============================================================================
A.B.E.L. Project - Token verification and user extraction
===============================================================================
"""

import logging
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.supabase.auth import AuthUser, get_auth_service

logger = logging.getLogger(__name__)

# HTTP Bearer scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> AuthUser:
    """
    FastAPI dependency to get current authenticated user.

    Extracts and validates JWT token from Authorization header.

    Args:
        request: FastAPI request
        credentials: Bearer token credentials

    Returns:
        AuthUser: Authenticated user

    Raises:
        HTTPException: If not authenticated
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    auth_service = get_auth_service()

    try:
        user = await auth_service.get_user(token)
        return user
    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> Optional[AuthUser]:
    """
    FastAPI dependency to get optional user (no error if not authenticated).

    Args:
        credentials: Bearer token credentials

    Returns:
        AuthUser or None
    """
    if credentials is None:
        return None

    token = credentials.credentials
    auth_service = get_auth_service()

    try:
        return await auth_service.get_user(token)
    except Exception:
        return None


def require_auth(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """
    Dependency that requires authentication.

    Use as: current_user: AuthUser = Depends(require_auth)
    """
    return user
