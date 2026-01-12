"""
===============================================================================
MIDDLEWARE.PY - Security Middleware
===============================================================================
A.B.E.L. Project - FastAPI Security Middleware
Implements security headers, CORS, and request validation
===============================================================================
"""

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.security import SECURITY_HEADERS


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Implements OWASP security best practices:
    - HSTS (HTTP Strict Transport Security)
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    - Permissions-Policy
    - Content-Security-Policy
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Add all security headers
        for header_name, header_value in SECURITY_HEADERS.items():
            response.headers[header_name] = header_value

        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID for tracing.

    Generates or forwards X-Request-ID header for distributed tracing
    and debugging purposes.
    """

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Add request ID to request state and response headers.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response with X-Request-ID header
        """
        import uuid

        # Use existing request ID or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store in request state for logging
        request.state.request_id = request_id

        response = await call_next(request)

        # Add to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate Content-Type header on POST/PUT requests.

    Ensures that requests with body content have appropriate Content-Type
    to prevent content-type confusion attacks.
    """

    ALLOWED_CONTENT_TYPES = [
        "application/json",
        "multipart/form-data",
        "application/x-www-form-urlencoded",
    ]

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Validate Content-Type header for body-bearing requests.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            Response or 415 error if Content-Type invalid
        """
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")

            # Skip validation for requests without body
            content_length = request.headers.get("Content-Length", "0")
            if content_length != "0" and content_type:
                # Extract base content type (without charset, boundary, etc.)
                base_content_type = content_type.split(";")[0].strip().lower()

                if base_content_type not in self.ALLOWED_CONTENT_TYPES:
                    from fastapi.responses import JSONResponse

                    return JSONResponse(
                        status_code=415,
                        content={
                            "detail": "Unsupported Media Type",
                            "allowed": self.ALLOWED_CONTENT_TYPES,
                        },
                    )

        return await call_next(request)
