"""
===============================================================================
EXCEPTIONS.PY - Custom Exceptions
===============================================================================
A.B.E.L. Project - Application Exception Classes
Provides structured error handling without exposing internals
===============================================================================
"""

from typing import Any, Dict


class ABELException(Exception):
    """Base exception for A.B.E.L. application."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class AuthenticationError(ABELException):
    """Raised when authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(ABELException):
    """Raised when user lacks permission for an action."""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class ValidationError(ABELException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(ABELException):
    """Raised when requested resource is not found."""

    def __init__(
        self,
        message: str = "Resource not found",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details,
        )


class RateLimitError(ABELException):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int = 60,
    ) -> None:
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after},
        )


class ExternalServiceError(ABELException):
    """Raised when external service call fails."""

    def __init__(
        self,
        service: str,
        message: str = "External service unavailable",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=503,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **(details or {})},
        )


class GeminiError(ExternalServiceError):
    """Raised when Gemini API call fails."""

    def __init__(
        self,
        message: str = "Gemini AI service unavailable",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            service="gemini",
            message=message,
            details=details,
        )


class SupabaseError(ExternalServiceError):
    """Raised when Supabase call fails."""

    def __init__(
        self,
        message: str = "Database service unavailable",
        details: Dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            service="supabase",
            message=message,
            details=details,
        )
