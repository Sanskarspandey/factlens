"""Vector search and embedding package initialization."""
from app.services.vector.base import BaseEmbeddingProvider, BaseVectorStore
from app.services.vector.embeddings import (
    SentenceTransformerEmbeddingProvider,
    embedding_service,
    build_fact_semantic_representation
)
from app.services.vector.chroma_store import ChromaVectorStore, vector_store

__all__ = [
    "BaseEmbeddingProvider",
    "BaseVectorStore",
    "SentenceTransformerEmbeddingProvider",
    "embedding_service",
    "build_fact_semantic_representation",
    "ChromaVectorStore",
    "vector_store",
]
