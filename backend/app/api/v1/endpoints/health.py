"""
===============================================================================
HEALTH.PY - Health Check Endpoints
===============================================================================
A.B.E.L. Project - Service Health Monitoring
===============================================================================
"""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check() -> dict:
    """
    Basic health check endpoint.

    Returns simple status for load balancers.
    No authentication required.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/live")
async def liveness_check() -> dict:
    """
    Kubernetes liveness probe endpoint.

    Indicates if the application is running.
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness_check() -> dict:
    """
    Kubernetes readiness probe endpoint.

    Checks if all dependencies are available.
    """
    # TODO: Add actual dependency checks
    checks = {
        "database": "ok",
        "gemini": "ok",
        "cache": "ok",
    }

    all_ok = all(v == "ok" for v in checks.values())

    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
    }
