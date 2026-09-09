"""Abstract base interfaces for Embedding and Vector Storage services."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseEmbeddingProvider(ABC):
    """Generic interface for embedding providers (SentenceTransformers, Local, API)."""

    @abstractmethod
    def encode_text(self, text: str) -> List[float]:
        """Encodes a single text string into a dense vector."""
        pass

    @abstractmethod
    def encode_many(self, texts: List[str]) -> List[List[float]]:
        """Encodes multiple text strings into a list of dense vectors."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Returns the embedding dimension size (e.g. 384 for all-MiniLM-L6-v2)."""
        pass


class BaseVectorStore(ABC):
    """Generic interface for vector indexing and semantic retrieval of facts."""

    @abstractmethod
    def add_facts(self, items: List[Dict[str, Any]]) -> List[str]:
        """
        Indexes fact embeddings and metadata into vector collection.
        Each item is: {"fact_id": str, "embedding": List[float], "metadata": dict, "document": str}
        """
        pass

    @abstractmethod
    def query_similar_facts(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Finds semantically similar facts by embedding vector."""
        pass

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> None:
        """Deletes all indexed vectors for a specific document."""
        pass

    @abstractmethod
    def delete_by_fact_id(self, fact_id: str) -> None:
        """Deletes vector for a single fact."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Returns total number of indexed vectors."""
        pass
