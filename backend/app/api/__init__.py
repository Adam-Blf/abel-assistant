"""
A.B.E.L - API Routes
"""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.voice import router as voice_router
from app.api.memory import router as memory_router
from app.api.websocket import router as ws_router

api_router = APIRouter()

# Include all routers
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice"])
api_router.include_router(memory_router, prefix="/memory", tags=["Memory"])
api_router.include_router(ws_router, prefix="/ws", tags=["WebSocket"])
