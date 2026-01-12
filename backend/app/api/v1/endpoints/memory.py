"""
===============================================================================
MEMORY.PY - Memory API Endpoints
===============================================================================
A.B.E.L. Project - Personal memory management
This is how A.B.E.L. learns from you!
===============================================================================
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Request

from app.core.security.auth import get_current_user
from app.core.security.rate_limiter import limiter
from app.schemas.requests.memory import (
    SearchMemoriesRequest,
    StoreMemoryRequest,
    UpdateMemoryRequest,
)
from app.schemas.responses.memory import (
    LearningResponse,
    MemoryListResponse,
    MemoryResponse,
    MemoryStatsResponse,
    SearchResultResponse,
    SearchResultsResponse,
)
from app.services.memory.vector_store import get_vector_store
from app.services.supabase.auth import AuthUser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/store", response_model=MemoryResponse)
@limiter.limit("30/minute")
async def store_memory(
    request: Request,
    data: StoreMemoryRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> MemoryResponse:
    """
    Store a new memory about the user.

    This is how you teach A.B.E.L. about yourself!

    Categories:
    - preference: Your likes/dislikes
    - habit: Your routines and behaviors
    - knowledge: Facts about you (job, skills, etc.)
    - context: Current projects, situations
    - personality: Communication preferences

    Args:
        request: FastAPI request
        data: Memory data
        current_user: Authenticated user

    Returns:
        Created memory
    """
    logger.info(f"Storing memory for user {current_user.id}: {data.category}")

    vector_store = get_vector_store()
    entry = await vector_store.store_memory(
        user_id=current_user.id,
        category=data.category,
        content=data.content,
        importance=data.importance,
        metadata=data.metadata,
    )

    return MemoryResponse(
        id=entry.id,
        category=entry.category,
        content=entry.content,
        importance=entry.importance,
        access_count=entry.access_count,
        created_at=entry.created_at,
        metadata=entry.metadata,
    )


@router.post("/search", response_model=SearchResultsResponse)
@limiter.limit("60/minute")
async def search_memories(
    request: Request,
    data: SearchMemoriesRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> SearchResultsResponse:
    """
    Search memories by semantic similarity.

    Find relevant memories based on meaning, not just keywords.

    Args:
        request: FastAPI request
        data: Search parameters
        current_user: Authenticated user

    Returns:
        Search results with similarity scores
    """
    logger.debug(f"Searching memories for user {current_user.id}: {data.query}")

    vector_store = get_vector_store()
    results = await vector_store.search_memories(
        user_id=current_user.id,
        query=data.query,
        category=data.category,
        limit=data.limit,
        min_similarity=data.min_similarity,
    )

    return SearchResultsResponse(
        results=[
            SearchResultResponse(
                memory=MemoryResponse(
                    id=r.entry.id,
                    category=r.entry.category,
                    content=r.entry.content,
                    importance=r.entry.importance,
                    access_count=r.entry.access_count,
                    created_at=r.entry.created_at,
                    similarity=r.similarity,
                    metadata=r.entry.metadata,
                ),
                similarity=r.similarity,
            )
            for r in results
        ],
        query=data.query,
        total_found=len(results),
    )


@router.get("/list", response_model=MemoryListResponse)
async def list_memories(
    category: Optional[str] = None,
    limit: int = 20,
    current_user: AuthUser = Depends(get_current_user),
) -> MemoryListResponse:
    """
    List all memories for the current user.

    Args:
        category: Filter by category (optional)
        limit: Maximum memories to return
        current_user: Authenticated user

    Returns:
        List of memories
    """
    vector_store = get_vector_store()
    memories = await vector_store.get_user_memories(
        user_id=current_user.id,
        category=category,
        limit=limit,
    )

    # Calculate category counts
    category_counts: dict = {}
    for mem in memories:
        category_counts[mem.category] = category_counts.get(mem.category, 0) + 1

    return MemoryListResponse(
        memories=[
            MemoryResponse(
                id=m.id,
                category=m.category,
                content=m.content,
                importance=m.importance,
                access_count=m.access_count,
                created_at=m.created_at,
                metadata=m.metadata,
            )
            for m in memories
        ],
        total=len(memories),
        category_counts=category_counts,
    )


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    current_user: AuthUser = Depends(get_current_user),
) -> MemoryStatsResponse:
    """
    Get memory statistics for the current user.

    Returns:
        Memory statistics
    """
    vector_store = get_vector_store()
    memories = await vector_store.get_user_memories(
        user_id=current_user.id,
        limit=100,
    )

    if not memories:
        return MemoryStatsResponse(
            total_memories=0,
            categories={},
            avg_importance=0.0,
        )

    # Calculate stats
    categories: dict = {}
    total_importance = 0.0
    most_accessed = memories[0]
    latest = memories[0]

    for mem in memories:
        categories[mem.category] = categories.get(mem.category, 0) + 1
        total_importance += mem.importance
        if mem.access_count > most_accessed.access_count:
            most_accessed = mem
        if mem.created_at > latest.created_at:
            latest = mem

    return MemoryStatsResponse(
        total_memories=len(memories),
        categories=categories,
        avg_importance=total_importance / len(memories),
        most_accessed=MemoryResponse(
            id=most_accessed.id,
            category=most_accessed.category,
            content=most_accessed.content,
            importance=most_accessed.importance,
            access_count=most_accessed.access_count,
            created_at=most_accessed.created_at,
            metadata=most_accessed.metadata,
        ),
        latest=MemoryResponse(
            id=latest.id,
            category=latest.category,
            content=latest.content,
            importance=latest.importance,
            access_count=latest.access_count,
            created_at=latest.created_at,
            metadata=latest.metadata,
        ),
    )


@router.patch("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    data: UpdateMemoryRequest,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """
    Update a memory's importance or content.

    Args:
        memory_id: Memory ID to update
        data: Update data
        current_user: Authenticated user

    Returns:
        Updated memory
    """
    vector_store = get_vector_store()

    if data.importance is not None:
        await vector_store.update_memory_importance(memory_id, data.importance)

    # Return success message
    return {"message": "Memory updated", "memory_id": memory_id}


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """
    Delete a specific memory.

    Args:
        memory_id: Memory ID to delete
        current_user: Authenticated user

    Returns:
        Confirmation message
    """
    logger.info(f"Deleting memory {memory_id} for user {current_user.id}")

    vector_store = get_vector_store()
    await vector_store.delete_memory(memory_id, current_user.id)

    return {"message": "Memory deleted", "memory_id": memory_id}


@router.delete("/clear/all")
async def clear_all_memories(
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    """
    Clear ALL memories for the current user.

    WARNING: This cannot be undone!

    Returns:
        Confirmation message
    """
    logger.warning(f"Clearing all memories for user {current_user.id}")

    vector_store = get_vector_store()
    await vector_store.clear_user_memories(current_user.id)

    return {
        "message": "All memories cleared",
        "user_id": current_user.id,
    }
