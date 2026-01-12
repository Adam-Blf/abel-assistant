"""
===============================================================================
CHAT.PY - Chat Request Schemas
===============================================================================
A.B.E.L. Project - Pydantic Request Validation for Chat
Strict input validation to prevent injection attacks
===============================================================================
"""

import re
from typing import List, Literal

from pydantic import BaseModel, Field, field_validator


class MessageHistory(BaseModel):
    """Single message in conversation history."""

    role: Literal["user", "assistant"] = Field(
        ..., description="Message role: 'user' or 'assistant'"
    )
    content: str = Field(
        ..., min_length=1, max_length=10000, description="Message content"
    )


class ChatRequest(BaseModel):
    """
    Chat request payload.

    Validates user input before processing.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User's message to the AI",
    )
    history: List[MessageHistory] | None = Field(
        default=None,
        max_length=50,  # Max 50 messages in history
        description="Optional conversation history",
    )
    system_prompt: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional system instruction",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """
        Validate and sanitize message content.

        - Strips whitespace
        - Checks for empty content
        - Basic injection prevention
        """
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")

        # Remove potential script tags (basic XSS prevention)
        v = re.sub(r"<script[^>]*>.*?</script>", "", v, flags=re.IGNORECASE | re.DOTALL)

        return v

    @field_validator("system_prompt")
    @classmethod
    def validate_system_prompt(cls, v: str | None) -> str | None:
        """Validate system prompt if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Hello, what can you help me with today?",
                "history": [
                    {"role": "user", "content": "Hi"},
                    {"role": "assistant", "content": "Hello! How can I assist you?"},
                ],
            }
        }
    }
