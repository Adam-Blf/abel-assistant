"""
===============================================================================
MAIN.PY - FastAPI Application Entry Point
===============================================================================
A.B.E.L. Project - Backend API Server
Full security middleware chain with Gemini AI integration
===============================================================================
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config.settings import get_settings
from app.config.security import CORS_CONFIG
from app.core.exceptions import ABELException
from app.core.security.middleware import (
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.security.rate_limiter import limiter

# Get settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    NEVER crashes - all initialization errors are caught and logged.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} API server")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Mock mode allowed: {settings.allow_mock_mode}")

    # Initialize external tools (never crash)
    try:
        from app.services.tools import initialize_tools
        initialize_tools()
        logger.info("External tools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize external tools: {e}")
        if settings.allow_mock_mode:
            logger.warning("Continuing without external tools (mock mode)")
        else:
            logger.critical("External tools required but initialization failed")

    # Check service availability
    service_status = {}
    try:
        from app.services.supabase.client import get_supabase_client
        from app.services.gemini.client import get_gemini_client

        supabase_client = get_supabase_client()
        gemini_client = get_gemini_client()

        service_status["supabase"] = "available" if supabase_client.is_available else "mock_mode"
        service_status["gemini"] = "available" if gemini_client.is_available else "mock_mode"

        logger.info(f"Service status: {service_status}")
    except Exception as e:
        logger.error(f"Failed to check service status: {e}")
        service_status["status"] = "unknown"

    # Store service status in app state
    app.state.service_status = service_status

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name} API server")


# =============================================================================
# CREATE APPLICATION
# =============================================================================

app = FastAPI(
    title=f"{settings.app_name} API",
    description="A.B.E.L. - Assistant IA Mobile Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# =============================================================================
# MIDDLEWARE CHAIN (Order matters!)
# =============================================================================

# 1. Request ID (first - for tracing)
app.add_middleware(RequestIDMiddleware)

# 2. Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# 3. Trusted Host
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.trusted_hosts_list,
)

# 4. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
    max_age=CORS_CONFIG["max_age"],
)

# 5. Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================


@app.exception_handler(ABELException)
async def abel_exception_handler(request: Request, exc: ABELException) -> JSONResponse:
    """Handle custom ABEL exceptions."""
    logger.warning(f"ABELException: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions without exposing internals."""
    logger.exception(f"Unhandled exception: {type(exc).__name__}")

    # Don't expose internal errors in production
    if settings.is_production:
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )

    # In development, provide more details
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": str(exc),
            "type": type(exc).__name__,
        },
    )


# =============================================================================
# HEALTH ENDPOINTS
# =============================================================================


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns basic health status for load balancers and monitoring.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0",
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check(request: Request) -> dict:
    """
    Readiness check endpoint.

    Verifies all dependencies are available.
    """
    service_status = getattr(request.app.state, "service_status", {})

    # Determine overall readiness
    is_ready = all(
        status in ["available", "mock_mode"]
        for status in service_status.values()
    )

    return {
        "status": "ready" if is_ready else "degraded",
        "services": service_status,
        "message": "Some services running in mock mode" if not is_ready else "All services operational",
    }


# =============================================================================
# API ROUTER REGISTRATION
# =============================================================================

# Import and register API routers
from app.api.v1.router import api_router

app.include_router(api_router, prefix="/api/v1")


# =============================================================================
# ROOT ENDPOINT
# =============================================================================


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "description": "A.B.E.L. - Assistant IA Mobile Backend API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else None,
        "health": "/health",
    }
