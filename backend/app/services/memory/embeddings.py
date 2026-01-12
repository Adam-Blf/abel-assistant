"""
===============================================================================
EMBEDDINGS.PY - Gemini Embeddings Service
===============================================================================
A.B.E.L. Project - Convert text to vector embeddings
Uses Google's Gemini embedding model
===============================================================================
"""

import logging
from typing import List, Optional

import google.generativeai as genai

from app.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

# Embedding model configuration
EMBEDDING_MODEL = "models/embedding-001"
EMBEDDING_DIMENSION = 768


class EmbeddingsService:
    """
    Service for generating text embeddings using Gemini.

    Embeddings are used for:
    - Semantic search in user memories
    - Finding similar conversations
    - Understanding context relevance
    """

    def __init__(self, settings: Optional[Settings] = None):
        """Initialize embeddings service."""
        self.settings = settings or get_settings()
        self._configured = False
        self._configure()

    def _configure(self) -> None:
        """Configure Gemini API."""
        if not self._configured:
            genai.configure(
                api_key=self.settings.gemini_api_key.get_secret_value()
            )
            self._configured = True
            logger.info("Embeddings service configured")

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise

    async def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Uses different task_type for better retrieval.

        Args:
            query: Search query

        Returns:
            List of floats (768 dimensions)
        """
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query",
            )
            return result["embedding"]
        except Exception as e:
            logger.error(f"Query embedding error: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings
        """
        try:
            embeddings = []
            for text in texts:
                embedding = await self.embed_text(text)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding error: {e}")
            raise


# Global instance
_embeddings_service: Optional[EmbeddingsService] = None


def get_embeddings_service() -> EmbeddingsService:
    """Get or create EmbeddingsService singleton."""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service
