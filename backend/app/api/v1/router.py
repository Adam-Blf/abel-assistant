"""
===============================================================================
ROUTER.PY - API v1 Router
===============================================================================
A.B.E.L. Project - Main API Router
Aggregates all v1 endpoint routers
===============================================================================
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, health, memory, vision, voice

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(chat.router)
api_router.include_router(memory.router)
api_router.include_router(voice.router)
api_router.include_router(vision.router)

# Future routers:
# api_router.include_router(tools.router)
