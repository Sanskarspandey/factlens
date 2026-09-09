"""Embedding provider implementation and semantic text representations."""
import math
import hashlib
from typing import List, Optional, Any
from app.services.vector.base import BaseEmbeddingProvider
from app.core.config import settings
from app.core.logging import logger


def build_fact_semantic_representation(fact: Any) -> str:
    """
    Constructs a comprehensive semantic string from structured fact dimensions.
    Captures entity, metric/attribute, natural language statement, normalized value, time period, scope, and definition.
    """
    entity = getattr(fact, "entity", None) or "Unknown Entity"
    attribute = getattr(fact, "attribute", None) or "General Metric"
    statement = getattr(fact, "statement", None) or ""
    value_str = getattr(fact, "normalized_value_str", None) or getattr(fact, "raw_value", None) or ""
    period = getattr(fact, "time_period", None) or ""
    scope = getattr(fact, "scope", None) or ""
    definition = getattr(fact, "definition", None) or ""
    geography = getattr(fact, "geography", None) or ""

    parts = [f"Entity: {entity}", f"Metric: {attribute}"]
    if value_str:
        parts.append(f"Value: {value_str}")
    if period:
        parts.append(f"Period: {period}")
    if scope:
        parts.append(f"Scope: {scope}")
    if geography:
        parts.append(f"Geography: {geography}")
    if definition:
        parts.append(f"Definition: {definition}")
    if statement:
        parts.append(f"Claim: {statement}")

    return " | ".join(parts)


class SentenceTransformerEmbeddingProvider(BaseEmbeddingProvider):
    """
    Local embedding provider using SentenceTransformers (default: all-MiniLM-L6-v2).
    Includes a deterministic hash-embedding fallback if sentence_transformers is offline.
    """

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model_name = model_name
        self._model = None
        self._dimension = 384
        self._use_fallback = False

    def _get_model(self):
        if self._model is None and not self._use_fallback:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local SentenceTransformer model: {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
                dim_fn = getattr(self._model, "get_embedding_dimension", getattr(self._model, "get_sentence_embedding_dimension", None))
                self._dimension = dim_fn() if dim_fn else 384
                logger.info(f"SentenceTransformer loaded successfully (dimension={self._dimension}).")
            except Exception as e:
                logger.warning(f"Could not load SentenceTransformer ({e}). Using deterministic embedding fallback.")
                self._use_fallback = True
        return self._model

    def encode_text(self, text: str) -> List[float]:
        return self.encode_many([text])[0]

    def encode_many(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        model = self._get_model()
        if model is not None and not self._use_fallback:
            try:
                embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
                return [emb.tolist() for emb in embeddings]
            except Exception as e:
                logger.error(f"SentenceTransformer encoding failed: {e}")

        # Deterministic hashing embedding fallback
        return [self._hash_embedding(t) for t in texts]

    def _hash_embedding(self, text: str) -> List[float]:
        """Generates a normalized 384-dimensional deterministic pseudo-semantic vector."""
        words = text.lower().split()
        vec = [0.0] * self._dimension
        for word in words:
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            for i in range(16):
                idx = (h + i * 23) % self._dimension
                val = ((h >> (i * 4)) & 0xF) - 7.5
                vec[idx] += val

        # Normalize L2 norm
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0
        return vec

    def get_dimension(self) -> int:
        return self._dimension


# Global singleton instance
embedding_service = SentenceTransformerEmbeddingProvider()
