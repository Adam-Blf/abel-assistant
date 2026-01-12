"""
===============================================================================
CHAT.PY - Chat API Endpoints
===============================================================================
A.B.E.L. Project - Chat Endpoints with Gemini + RAG Integration
Personalized responses using user memories
===============================================================================
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.config.settings import Settings, get_settings
from app.core.security.auth import get_optional_user
from app.core.security.rate_limiter import limiter
from app.schemas.requests.chat import ChatRequest
from app.schemas.responses.chat import ChatResponse
from app.services.gemini.client import GeminiClient, get_gemini_client
from app.services.memory.rag import get_rag_pipeline
from app.services.supabase.auth import AuthUser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    chat_request: ChatRequest,
    current_user: Optional[AuthUser] = Depends(get_optional_user),
    gemini: GeminiClient = Depends(get_gemini_client),
    settings: Settings = Depends(get_settings),
) -> ChatResponse:
    """
    Send a message to A.B.E.L. and receive a personalized response.

    If authenticated, A.B.E.L. uses your memories to personalize responses
    and learns from the conversation.

    Rate limited to 30 requests per minute.

    Args:
        request: FastAPI request (for rate limiting)
        chat_request: Validated chat request
        current_user: Optional authenticated user
        gemini: Gemini client instance
        settings: Application settings

    Returns:
        ChatResponse with AI-generated personalized message
    """
    logger.info(f"Chat request received: {len(chat_request.message)} chars")

    # Format history if provided
    history = None
    if chat_request.history:
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in chat_request.history
        ]

    # If user is authenticated, use RAG for personalized response
    if current_user:
        logger.info(f"Using RAG for authenticated user: {current_user.id}")
        rag = get_rag_pipeline()

        try:
            rag_response = await rag.generate_with_context(
                user_id=current_user.id,
                message=chat_request.message,
                history=history,
            )

            # Log new learnings
            if rag_response.new_learnings:
                logger.info(
                    f"Extracted {len(rag_response.new_learnings)} new learnings"
                )

            return ChatResponse(
                message=rag_response.response,
                role="assistant",
                timestamp=datetime.utcnow(),
                model=settings.gemini_model_chat,
                context_used=len(rag_response.context_used) > 0,
            )

        except Exception as e:
            logger.warning(f"RAG failed, falling back to standard: {e}")
            # Fall through to standard generation

    # Standard generation (no personalization)
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
        context_used=False,
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
