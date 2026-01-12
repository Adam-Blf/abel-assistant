"""
===============================================================================
MEMORY REQUESTS - Memory Request Schemas
===============================================================================
A.B.E.L. Project - Pydantic models for memory endpoints
===============================================================================
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class StoreMemoryRequest(BaseModel):
    """Request to store a new memory."""

    category: str = Field(
        ...,
        pattern="^(preference|habit|knowledge|context|personality)$",
        description="Memory category",
    )
    content: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Memory content",
    )
    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score (0-1)",
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata",
    )


class SearchMemoriesRequest(BaseModel):
    """Request to search memories."""

    query: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Search query",
    )
    category: Optional[str] = Field(
        default=None,
        pattern="^(preference|habit|knowledge|context|personality)$",
        description="Filter by category",
    )
    limit: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum results",
    )
    min_similarity: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold",
    )


class UpdateMemoryRequest(BaseModel):
    """Request to update a memory."""

    importance: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="New importance score",
    )
    content: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=2000,
        description="New content",
    )
