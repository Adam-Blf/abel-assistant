"""
===============================================================================
MEMORY SERVICES - Init
===============================================================================
A.B.E.L. Personal Memory System - The core of learning
===============================================================================
"""

from app.services.memory.embeddings import (
    EMBEDDING_DIMENSION,
    EmbeddingsService,
    get_embeddings_service,
)
from app.services.memory.rag import (
    RAGContext,
    RAGPipeline,
    RAGResponse,
    get_rag_pipeline,
)
from app.services.memory.vector_store import (
    MemoryEntry,
    SearchResult,
    VectorStore,
    get_vector_store,
)

__all__ = [
    # Embeddings
    "EmbeddingsService",
    "get_embeddings_service",
    "EMBEDDING_DIMENSION",
    # Vector Store
    "VectorStore",
    "get_vector_store",
    "MemoryEntry",
    "SearchResult",
    # RAG Pipeline
    "RAGPipeline",
    "get_rag_pipeline",
    "RAGContext",
    "RAGResponse",
]
