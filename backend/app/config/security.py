"""
===============================================================================
SECURITY.PY - Security Configuration
===============================================================================
A.B.E.L. Project - Core Security Settings
CRITICAL: All security headers and middleware configuration
===============================================================================
"""

from typing import Dict, List

# =============================================================================
# SECURITY HEADERS (HSTS, X-Frame-Options, etc.)
# =============================================================================

SECURITY_HEADERS: Dict[str, str] = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(self), camera=(self)",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
}

# =============================================================================
# CORS CONFIGURATION (Strict)
# =============================================================================

CORS_CONFIG: Dict[str, object] = {
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type", "X-Request-ID"],
    "max_age": 600,  # 10 minutes
}

# =============================================================================
# TRUSTED HOSTS (Default)
# =============================================================================

DEFAULT_TRUSTED_HOSTS: List[str] = [
    "localhost",
    "127.0.0.1",
]

# =============================================================================
# RATE LIMITING
# =============================================================================

RATE_LIMITS: Dict[str, str] = {
    "default": "100/minute",
    "auth_login": "5/minute",
    "auth_register": "3/minute",
    "chat_message": "30/minute",
    "voice": "10/minute",
    "vision": "5/minute",
}

# =============================================================================
# SESSION CONFIGURATION
# =============================================================================

SESSION_CONFIG: Dict[str, int] = {
    "timeout_minutes": 15,  # CRITICAL: 15 min timeout
    "refresh_threshold_minutes": 5,
    "max_sessions_per_user": 3,
}

# =============================================================================
# PASSWORD REQUIREMENTS
# =============================================================================

PASSWORD_CONFIG: Dict[str, object] = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digit": True,
    "require_special": False,
}

# =============================================================================
# JWT CONFIGURATION
# =============================================================================

JWT_CONFIG: Dict[str, object] = {
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
}
