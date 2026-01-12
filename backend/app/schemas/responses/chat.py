"""
===============================================================================
CHAT.PY - Chat Response Schemas
===============================================================================
A.B.E.L. Project - Pydantic Response Models for Chat
===============================================================================
"""

from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """
    Chat response payload.

    Returns AI-generated response with metadata.
    """

    message: str = Field(..., description="AI-generated response")
    role: Literal["assistant"] = Field(default="assistant", description="Response role")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    model: str = Field(..., description="Model used for generation")
    context_used: bool = Field(
        default=False, description="Whether personal context was used (RAG)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Hello! I'm A.B.E.L., your AI assistant. How can I help you today?",
                "role": "assistant",
                "timestamp": "2026-01-12T10:30:00Z",
                "model": "gemini-1.5-flash",
                "context_used": True,
            }
        }
    }


class ConversationMessage(BaseModel):
    """Single message in a conversation."""

    id: str = Field(..., description="Message unique ID")
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")


class ConversationResponse(BaseModel):
    """Full conversation response."""

    conversation_id: str = Field(..., description="Conversation unique ID")
    messages: List[ConversationMessage] = Field(..., description="List of messages")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")
