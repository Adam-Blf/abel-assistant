"""
A.B.E.L - Health Check Endpoints
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.redis import redis_client
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "ABEL ONLINE",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "environment": settings.app_env,
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Detailed health check with service status."""

    services = {
        "api": {"status": "healthy", "latency_ms": 0},
        "database": {"status": "unknown", "latency_ms": 0},
        "redis": {"status": "unknown", "latency_ms": 0},
        "qdrant": {"status": "unknown", "latency_ms": 0},
    }

    # Check PostgreSQL
    try:
        start = datetime.utcnow()
        await db.execute(text("SELECT 1"))
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        services["database"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = {"status": "unhealthy", "error": str(e)}

    # Check Redis
    try:
        start = datetime.utcnow()
        await redis_client.client.ping()
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        services["redis"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        services["redis"] = {"status": "unhealthy", "error": str(e)}

    # Check Qdrant
    try:
        from qdrant_client import QdrantClient

        start = datetime.utcnow()
        client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        client.get_collections()
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        services["qdrant"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        logger.error(f"Qdrant health check failed: {e}")
        services["qdrant"] = {"status": "unhealthy", "error": str(e)}

    # Determine overall status
    all_healthy = all(s["status"] == "healthy" for s in services.values())

    return {
        "status": "ABEL ONLINE" if all_healthy else "DEGRADED",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": services,
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, str]:
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Kubernetes liveness probe."""
    return {"status": "alive"}
