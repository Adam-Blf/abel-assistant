"""
A.B.E.L - API Dependencies
=============================
Dependances communes pour les endpoints API.
"""

from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import verify_token, get_current_user, require_auth
from app.core.logging import logger


# ============================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================

security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token (optional).
    Returns None if no valid token provided.

    Usage:
        @router.get("/endpoint")
        async def endpoint(user: Optional[Dict] = Depends(get_optional_user)):
            if user:
                # User is authenticated
                user_id = user.get("sub")
            else:
                # User is not authenticated, proceed as anonymous
    """
    if not credentials:
        return None

    payload = verify_token(credentials.credentials)
    if not payload:
        logger.warning("Invalid token provided")
        return None

    return payload


async def get_required_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Get current user from JWT token (required).
    Raises 401 if no valid token provided.

    Usage:
        @router.get("/protected")
        async def protected(user: Dict = Depends(get_required_user)):
            user_id = user.get("sub")
            # User is guaranteed to be authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


# Re-export for convenience
__all__ = [
    "get_optional_user",
    "get_required_user",
    "get_current_user",  # From security module
    "require_auth",       # From security module
]
