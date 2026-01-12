"""
===============================================================================
CHAT.PY - Chat API Endpoints
===============================================================================
A.B.E.L. Project - Chat Endpoints with Gemini Integration
Rate limited and validated
===============================================================================
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Request

from app.config.settings import Settings, get_settings
from app.core.security.rate_limiter import limiter
from app.schemas.requests.chat import ChatRequest
from app.schemas.responses.chat import ChatResponse
from app.services.gemini.client import GeminiClient, get_gemini_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    gemini: GeminiClient = Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """
    Send a message to A.B.E.L. and receive a response.

    Rate limited to 30 requests per minute.

    Args:
        request: FastAPI request (for rate limiting)
        chat_request: Validated chat request
        gemini: Gemini client instance
        settings: Application settings

    Returns:
        ChatResponse with AI-generated message
    """
    logger.info(f"Chat request received: {len(chat_request.message)} chars")

    # Format history if provided
    history = None
    if chat_request.history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_request.history
        ]

    # Generate response
    response_text = await gemini.generate_response(
        prompt=chat_request.message,
        history=history,
        system_instruction=chat_request.system_prompt,
    )

    logger.info(f"Chat response generated: {len(response_text)} chars")

    return ChatResponse(
        message=response_text,
        role="assistant",
        timestamp=datetime.utcnow(),
        model=settings.gemini_model_chat,
    )


@router.post("/stream")
@limiter.limit("30/minute")
async def stream_message(
    request: Request,
    chat_request: ChatRequest,
) -> dict:
    """
    Stream a response from A.B.E.L. (placeholder for WebSocket).

    Note: Real streaming will use WebSocket connection.
    This endpoint is a placeholder for REST-based streaming.
    """
    # TODO: Implement SSE or redirect to WebSocket
    return {
        "message": "Streaming not yet implemented. Use WebSocket at /ws/chat",
        "websocket_url": "/ws/chat",
    }
