"""
A.B.E.L - Memory Service (RAG with Qdrant)
"""

import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime

from openai import AsyncOpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct

from app.core.config import settings
from app.core.logging import logger


class MemoryService:
    """
    Service for storing and retrieving memories using RAG.

    Uses:
    - OpenAI text-embedding-3-small for vector embeddings
    - Qdrant for vector storage and similarity search
    """

    EMBEDDING_DIMENSION = 1536  # text-embedding-3-small dimension

    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.qdrant_client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )
        self.collection_name = settings.qdrant_collection
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Ensure the Qdrant collection exists."""
        try:
            collections = self.qdrant_client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)

            if not exists:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.debug(f"Qdrant collection exists: {self.collection_name}")
        except Exception as e:
            logger.warning(f"Could not connect to Qdrant: {e}")

    async def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text using OpenAI."""
        response = await self.openai_client.embeddings.create(
            model=settings.openai_embedding_model,
            input=text,
        )
        return response.data[0].embedding

    async def store_memory(
        self,
        text: str,
        memory_type: str = "conversation",
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Store a memory in the vector database.

        Args:
            text: The content to store
            memory_type: Type of memory (conversation, fact, preference, etc.)
            source: Source of the memory
            tags: List of tags for categorization
            importance: Importance score (0-1)
            metadata: Additional metadata

        Returns:
            Dict with memory ID and status
        """
        try:
            # Generate unique ID
            memory_id = str(uuid.uuid4())

            # Get embedding
            embedding = await self._get_embedding(text)

            # Prepare payload
            payload = {
                "content": text,
                "memory_type": memory_type,
                "source": source,
                "tags": tags or [],
                "importance": importance,
                "created_at": datetime.utcnow().isoformat(),
                "access_count": 0,
                **(metadata or {}),
            }

            # Store in Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=memory_id,
                        vector=embedding,
                        payload=payload,
                    )
                ],
            )

            logger.info(f"Stored memory: {memory_id} ({memory_type})")

            return {
                "id": memory_id,
                "status": "stored",
                "memory_type": memory_type,
            }

        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            raise

    async def recall_memory(
        self,
        query: str,
        limit: int = 5,
        memory_type: Optional[str] = None,
        min_score: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories based on a query.

        Args:
            query: The search query
            limit: Maximum number of results
            memory_type: Filter by memory type
            min_score: Minimum similarity score

        Returns:
            List of relevant memories with scores
        """
        try:
            # Get query embedding
            query_embedding = await self._get_embedding(query)

            # Build filter if memory_type specified
            query_filter = None
            if memory_type:
                query_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="memory_type",
                            match=models.MatchValue(value=memory_type),
                        )
                    ]
                )

            # Search Qdrant
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit,
                score_threshold=min_score,
            )

            # Format results
            memories = []
            for result in results:
                memory = {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "memory_type": result.payload.get("memory_type", "unknown"),
                    "score": result.score,
                    "source": result.payload.get("source"),
                    "tags": result.payload.get("tags", []),
                    "created_at": result.payload.get("created_at"),
                    "importance": result.payload.get("importance", 0.5),
                }
                memories.append(memory)

                # Update access count (fire and forget)
                try:
                    self.qdrant_client.set_payload(
                        collection_name=self.collection_name,
                        payload={
                            "access_count": result.payload.get("access_count", 0) + 1,
                            "last_accessed": datetime.utcnow().isoformat(),
                        },
                        points=[result.id],
                    )
                except Exception:
                    pass

            logger.debug(f"Recalled {len(memories)} memories for query: {query[:50]}...")

            return memories

        except Exception as e:
            logger.error(f"Error recalling memory: {e}")
            return []

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a specific memory by ID."""
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[memory_id]),
            )
            logger.info(f"Deleted memory: {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get memory storage statistics."""
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            return {
                "total_memories": collection_info.points_count,
                "vectors_count": collection_info.vectors_count,
                "status": collection_info.status,
                "collection_name": self.collection_name,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}

    async def clear_all(self) -> None:
        """Clear all memories from the collection."""
        try:
            self.qdrant_client.delete_collection(self.collection_name)
            self._ensure_collection()
            logger.info("Cleared all memories")
        except Exception as e:
            logger.error(f"Error clearing memories: {e}")
            raise

    async def search_by_tags(
        self, tags: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memories by tags."""
        try:
            results = self.qdrant_client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    should=[
                        models.FieldCondition(
                            key="tags",
                            match=models.MatchAny(any=tags),
                        )
                    ]
                ),
                limit=limit,
            )

            memories = []
            for point in results[0]:
                memories.append({
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "memory_type": point.payload.get("memory_type"),
                    "tags": point.payload.get("tags", []),
                })

            return memories

        except Exception as e:
            logger.error(f"Error searching by tags: {e}")
            return []
