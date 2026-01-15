"""
A.B.E.L - Security Middleware & Utilities
=========================================
Fonctions de securite pour proteger l'application.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logging import logger


# ============================================================
# PASSWORD HASHING
# ============================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================
# JWT TOKENS
# ============================================================

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None


# ============================================================
# API KEY AUTHENTICATION
# ============================================================

def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()


# ============================================================
# REQUEST AUTHENTICATION
# ============================================================

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, Any]]:
    """
    Get current user from JWT token.
    Returns None if no valid token (for optional auth).
    """
    if not credentials:
        return None

    payload = verify_token(credentials.credentials)
    if not payload:
        return None

    return payload


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """
    Require authentication.
    Raises 401 if no valid token.
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


# ============================================================
# ERROR HANDLING (SECURE)
# ============================================================

def safe_error_response(
    status_code: int = 500,
    internal_message: str = "",
    public_message: str = "An error occurred",
) -> HTTPException:
    """
    Create a secure error response.
    Logs details internally but returns generic message to client.
    """
    if internal_message:
        logger.error(f"Error {status_code}: {internal_message}")

    # En production, ne jamais exposer les details
    if os.getenv("DEBUG", "false").lower() != "true":
        return HTTPException(status_code=status_code, detail=public_message)

    # En dev, on peut montrer plus de details
    return HTTPException(status_code=status_code, detail=internal_message or public_message)


# ============================================================
# INPUT SANITIZATION
# ============================================================

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    # Remove path separators and null bytes
    sanitized = filename.replace("/", "").replace("\\", "").replace("\x00", "")
    # Remove leading dots (hidden files)
    sanitized = sanitized.lstrip(".")
    # Limit length
    return sanitized[:255] if sanitized else "unnamed"


def sanitize_string(value: str, max_length: int = 10000) -> str:
    """Sanitize a string input."""
    if not value:
        return ""
    # Remove null bytes
    sanitized = value.replace("\x00", "")
    # Limit length
    return sanitized[:max_length]


# ============================================================
# RATE LIMITING (Simple in-memory)
# ============================================================

_rate_limit_store: Dict[str, list] = {}


def check_rate_limit(
    key: str,
    max_requests: int = 60,
    window_seconds: int = 60,
) -> bool:
    """
    Simple in-memory rate limiter.
    Returns True if request is allowed, False if rate limited.

    For production, use Redis-based rate limiting.
    """
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_seconds)

    if key not in _rate_limit_store:
        _rate_limit_store[key] = []

    # Clean old entries
    _rate_limit_store[key] = [
        ts for ts in _rate_limit_store[key]
        if ts > window_start
    ]

    # Check limit
    if len(_rate_limit_store[key]) >= max_requests:
        return False

    # Add current request
    _rate_limit_store[key].append(now)
    return True


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """Rate limiting decorator."""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Use IP as key
            client_ip = request.client.host if request.client else "unknown"
            key = f"{func.__name__}:{client_ip}"

            if not check_rate_limit(key, max_requests, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later.",
                )

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# SECURITY HEADERS MIDDLEWARE
# ============================================================

async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # XSS Protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Content Security Policy (adjust as needed)
    if os.getenv("DEBUG", "false").lower() != "true":
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    return response
