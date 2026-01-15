"""
A.B.E.L - Memory API Endpoints (RAG operations)
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.logging import logger
from app.brain.memory_service import MemoryService

router = APIRouter()


class StoreMemoryRequest(BaseModel):
    """Request to store a new memory."""

    content: str = Field(..., min_length=1, max_length=50000)
    memory_type: str = Field(
        default="fact",
        pattern="^(conversation|fact|preference|event|skill|document)$",
    )
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)


class MemoryResponse(BaseModel):
    """Memory item response."""

    id: str
    content: str
    memory_type: str
    score: Optional[float] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str


class SearchMemoryRequest(BaseModel):
    """Request to search memories."""

    query: str = Field(..., min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)
    memory_type: Optional[str] = None
    min_score: float = Field(default=0.5, ge=0.0, le=1.0)


@router.post("/store", response_model=MemoryResponse)
async def store_memory(request: StoreMemoryRequest):
    """
    Store a new memory in the vector database.

    The content will be embedded and stored for future retrieval.
    """
    try:
        memory_service = MemoryService()

        result = await memory_service.store_memory(
            text=request.content,
            memory_type=request.memory_type,
            source=request.source,
            tags=request.tags,
            importance=request.importance,
        )

        return MemoryResponse(
            id=result["id"],
            content=request.content,
            memory_type=request.memory_type,
            source=request.source,
            tags=request.tags,
            created_at=datetime.utcnow().isoformat(),
        )

    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.post("/search", response_model=List[MemoryResponse])
async def search_memories(request: SearchMemoryRequest):
    """
    Search for relevant memories using semantic similarity.

    Returns the most relevant memories based on the query.
    """
    try:
        memory_service = MemoryService()

        results = await memory_service.recall_memory(
            query=request.query,
            limit=request.limit,
            memory_type=request.memory_type,
            min_score=request.min_score,
        )

        return [
            MemoryResponse(
                id=r["id"],
                content=r["content"],
                memory_type=r.get("memory_type", "unknown"),
                score=r.get("score"),
                source=r.get("source"),
                tags=r.get("tags"),
                created_at=r.get("created_at", datetime.utcnow().isoformat()),
            )
            for r in results
        ]

    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/recall")
async def quick_recall(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=5, ge=1, le=20),
):
    """Quick memory recall (GET endpoint for convenience)."""
    try:
        memory_service = MemoryService()
        results = await memory_service.recall_memory(query=query, limit=limit)
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Error in quick recall: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    try:
        memory_service = MemoryService()
        success = await memory_service.delete_memory(memory_id)

        if not success:
            raise HTTPException(status_code=404, detail="Memory not found")

        return {"status": "deleted", "memory_id": memory_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.get("/stats")
async def memory_stats():
    """Get memory storage statistics."""
    try:
        memory_service = MemoryService()
        stats = await memory_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.post("/bulk-store")
async def bulk_store_memories(memories: List[StoreMemoryRequest]):
    """Store multiple memories at once."""
    try:
        memory_service = MemoryService()
        results = []

        for memory in memories:
            result = await memory_service.store_memory(
                text=memory.content,
                memory_type=memory.memory_type,
                source=memory.source,
                tags=memory.tags,
                importance=memory.importance,
            )
            results.append(result)

        return {
            "status": "success",
            "stored_count": len(results),
            "memory_ids": [r["id"] for r in results],
        }

    except Exception as e:
        logger.error(f"Error in bulk store: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")


@router.post("/clear")
async def clear_all_memories(confirm: bool = Query(default=False)):
    """
    Clear all memories from the vector database.

    Requires confirm=true to execute.
    """
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Set confirm=true to clear all memories. This action is irreversible.",
        )

    try:
        memory_service = MemoryService()
        await memory_service.clear_all()
        return {"status": "cleared", "message": "All memories have been deleted"}
    except Exception as e:
        logger.error(f"Error clearing memories: {e}")
        raise HTTPException(status_code=500, detail="An error occurred")
