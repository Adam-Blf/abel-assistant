"""
===============================================================================
MEMORY RESPONSES - Memory Response Schemas
===============================================================================
A.B.E.L. Project - Pydantic models for memory responses
===============================================================================
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MemoryResponse(BaseModel):
    """Single memory response."""

    id: str = Field(..., description="Memory ID")
    category: str = Field(..., description="Memory category")
    content: str = Field(..., description="Memory content")
    importance: float = Field(..., description="Importance score")
    access_count: int = Field(..., description="Number of times accessed")
    created_at: datetime = Field(..., description="Creation timestamp")
    similarity: Optional[float] = Field(None, description="Similarity score (for search)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class MemoryListResponse(BaseModel):
    """List of memories response."""

    memories: List[MemoryResponse]
    total: int = Field(..., description="Total count")
    category_counts: Optional[Dict[str, int]] = Field(
        None, description="Count per category"
    )


class SearchResultResponse(BaseModel):
    """Search result with similarity."""

    memory: MemoryResponse
    similarity: float = Field(..., description="Similarity score")


class SearchResultsResponse(BaseModel):
    """Search results response."""

    results: List[SearchResultResponse]
    query: str = Field(..., description="Original query")
    total_found: int = Field(..., description="Total results found")


class MemoryStatsResponse(BaseModel):
    """Memory statistics response."""

    total_memories: int
    categories: Dict[str, int]
    avg_importance: float
    most_accessed: Optional[MemoryResponse] = None
    latest: Optional[MemoryResponse] = None


class LearningResponse(BaseModel):
    """New learning extracted from conversation."""

    category: str
    content: str
    importance: float
    auto_extracted: bool = True
