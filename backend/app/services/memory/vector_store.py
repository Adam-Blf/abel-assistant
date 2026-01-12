"""
===============================================================================
VECTOR_STORE.PY - Vector Store Service
===============================================================================
A.B.E.L. Project - PostgreSQL pgvector storage and similarity search
===============================================================================
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.services.memory.embeddings import get_embeddings_service
from app.services.supabase.client import get_supabase_client

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A memory entry stored in the vector database."""

    id: str
    user_id: str
    category: str
    content: str
    importance: float
    access_count: int
    created_at: datetime
    metadata: Dict[str, Any]
    similarity: Optional[float] = None


@dataclass
class SearchResult:
    """Search result with similarity score."""

    entry: MemoryEntry
    similarity: float


class VectorStore:
    """
    Vector store for A.B.E.L. memories using pgvector.

    Provides:
    - Store memories with embeddings
    - Similarity search across memories
    - Memory importance scoring
    - Automatic embedding generation
    """

    def __init__(self):
        """Initialize vector store."""
        self.client = get_supabase_client().admin_client
        self.embeddings = get_embeddings_service()

    async def store_memory(
        self,
        user_id: str,
        category: str,
        content: str,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """
        Store a new memory with its embedding.

        Args:
            user_id: User ID
            category: Memory category (preference, habit, knowledge, context)
            content: Memory content
            importance: Importance score 0-1
            metadata: Additional metadata

        Returns:
            Created MemoryEntry
        """
        try:
            # Generate embedding
            embedding = await self.embeddings.embed_text(content)

            # Insert into database
            result = self.client.table("user_memories").insert({
                "user_id": user_id,
                "category": category,
                "content": content,
                "embedding": embedding,
                "importance": importance,
                "metadata": metadata or {},
            }).execute()

            if result.data:
                row = result.data[0]
                logger.info(f"Memory stored for user {user_id}: {category}")
                return MemoryEntry(
                    id=row["id"],
                    user_id=row["user_id"],
                    category=row["category"],
                    content=row["content"],
                    importance=row["importance"],
                    access_count=row["access_count"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=row["metadata"],
                )

            raise Exception("Failed to store memory")

        except Exception as e:
            logger.error(f"Store memory error: {e}")
            raise

    async def search_memories(
        self,
        user_id: str,
        query: str,
        category: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.7,
    ) -> List[SearchResult]:
        """
        Search memories by semantic similarity.

        Args:
            user_id: User ID
            query: Search query
            category: Filter by category (optional)
            limit: Max results
            min_similarity: Minimum similarity threshold

        Returns:
            List of SearchResults ordered by similarity
        """
        try:
            # Generate query embedding
            query_embedding = await self.embeddings.embed_query(query)

            # Build similarity search query
            # Using Supabase RPC for vector similarity
            rpc_params = {
                "query_embedding": query_embedding,
                "match_user_id": user_id,
                "match_threshold": min_similarity,
                "match_count": limit,
            }

            if category:
                rpc_params["match_category"] = category

            # Use raw SQL via RPC or direct query
            # For now, fetch and filter in Python (suboptimal but works)
            query_builder = (
                self.client.table("user_memories")
                .select("*")
                .eq("user_id", user_id)
            )

            if category:
                query_builder = query_builder.eq("category", category)

            result = query_builder.execute()

            if not result.data:
                return []

            # Calculate similarity scores
            results = []
            for row in result.data:
                if row.get("embedding"):
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(
                        query_embedding, row["embedding"]
                    )
                    if similarity >= min_similarity:
                        entry = MemoryEntry(
                            id=row["id"],
                            user_id=row["user_id"],
                            category=row["category"],
                            content=row["content"],
                            importance=row["importance"],
                            access_count=row["access_count"],
                            created_at=datetime.fromisoformat(row["created_at"]),
                            metadata=row["metadata"],
                            similarity=similarity,
                        )
                        results.append(SearchResult(entry=entry, similarity=similarity))

            # Sort by similarity and limit
            results.sort(key=lambda x: x.similarity, reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Search memories error: {e}")
            raise

    async def get_user_memories(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """
        Get all memories for a user.

        Args:
            user_id: User ID
            category: Filter by category (optional)
            limit: Max results

        Returns:
            List of MemoryEntry
        """
        try:
            query_builder = (
                self.client.table("user_memories")
                .select("*")
                .eq("user_id", user_id)
                .order("importance", desc=True)
                .limit(limit)
            )

            if category:
                query_builder = query_builder.eq("category", category)

            result = query_builder.execute()

            return [
                MemoryEntry(
                    id=row["id"],
                    user_id=row["user_id"],
                    category=row["category"],
                    content=row["content"],
                    importance=row["importance"],
                    access_count=row["access_count"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    metadata=row["metadata"],
                )
                for row in result.data
            ]

        except Exception as e:
            logger.error(f"Get memories error: {e}")
            raise

    async def update_memory_importance(
        self,
        memory_id: str,
        importance: float,
    ) -> None:
        """Update memory importance score."""
        try:
            self.client.table("user_memories").update({
                "importance": importance,
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", memory_id).execute()
        except Exception as e:
            logger.error(f"Update importance error: {e}")
            raise

    async def increment_access(self, memory_id: str) -> None:
        """Increment memory access count."""
        try:
            self.client.rpc(
                "increment_memory_access",
                {"memory_id": memory_id}
            ).execute()
        except Exception:
            # Fallback: manual update
            try:
                result = self.client.table("user_memories").select("access_count").eq("id", memory_id).single().execute()
                if result.data:
                    new_count = result.data["access_count"] + 1
                    self.client.table("user_memories").update({
                        "access_count": new_count,
                        "last_accessed": datetime.utcnow().isoformat(),
                    }).eq("id", memory_id).execute()
            except Exception as e:
                logger.warning(f"Increment access fallback error: {e}")

    async def delete_memory(self, memory_id: str, user_id: str) -> None:
        """Delete a memory."""
        try:
            self.client.table("user_memories").delete().eq(
                "id", memory_id
            ).eq("user_id", user_id).execute()
            logger.info(f"Memory deleted: {memory_id}")
        except Exception as e:
            logger.error(f"Delete memory error: {e}")
            raise

    async def clear_user_memories(self, user_id: str) -> None:
        """Clear all memories for a user."""
        try:
            self.client.table("user_memories").delete().eq(
                "user_id", user_id
            ).execute()
            logger.info(f"All memories cleared for user: {user_id}")
        except Exception as e:
            logger.error(f"Clear memories error: {e}")
            raise

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


# Global instance
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    """Get or create VectorStore singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
