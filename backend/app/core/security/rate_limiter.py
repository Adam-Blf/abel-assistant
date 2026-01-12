"""
===============================================================================
RATE_LIMITER.PY - Request Rate Limiting
===============================================================================
A.B.E.L. Project - slowapi Integration
Protects against brute-force and DoS attacks
===============================================================================
"""

from typing import Callable, TypeVar

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config.security import RATE_LIMITS

F = TypeVar("F", bound=Callable[..., object])


def get_client_ip(request: Request) -> str:
    """
    Extract client IP considering proxy headers.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address string
    """
    # Check X-Forwarded-For for proxied requests
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take first IP (original client)
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    return get_remote_address(request)


# Initialize limiter
limiter = Limiter(
    key_func=get_client_ip,
    default_limits=[RATE_LIMITS["default"]],
    strategy="fixed-window",
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> dict:
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: FastAPI request object
        exc: Rate limit exception

    Returns:
        Error response dictionary
    """
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail,
        },
        headers={"Retry-After": str(exc.detail)},
    )


# =============================================================================
# RATE LIMIT DECORATORS
# =============================================================================


def limit_auth(func: F) -> F:
    """Rate limit for auth endpoints: 5/minute"""
    return limiter.limit(RATE_LIMITS["auth_login"])(func)


def limit_chat(func: F) -> F:
    """Rate limit for chat endpoints: 30/minute"""
    return limiter.limit(RATE_LIMITS["chat_message"])(func)


def limit_voice(func: F) -> F:
    """Rate limit for voice endpoints: 10/minute"""
    return limiter.limit(RATE_LIMITS["voice"])(func)


def limit_vision(func: F) -> F:
    """Rate limit for vision endpoints: 5/minute"""
    return limiter.limit(RATE_LIMITS["vision"])(func)
