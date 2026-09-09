"""Persistent ChromaDB vector store implementation for facts."""
import os
from typing import List, Dict, Any, Optional
from app.services.vector.base import BaseVectorStore
from app.core.config import settings
from app.core.logging import logger


class ChromaVectorStore(BaseVectorStore):
    """Local persistent ChromaDB vector store for indexed facts."""

    def __init__(self, persist_dir: str = settings.VECTOR_STORE_DIR):
        self.persist_dir = persist_dir
        self.collection_name = "factlens_facts"
        self._client = None
        self._collection = None
        self._fallback_store: Dict[str, Dict[str, Any]] = {}
        self._use_fallback = False

    def _get_collection(self):
        if self._collection is None and not self._use_fallback:
            try:
                import chromadb
                os.makedirs(self.persist_dir, exist_ok=True)
                self._client = chromadb.PersistentClient(path=self.persist_dir)
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Connected to ChromaDB collection '{self.collection_name}' at {self.persist_dir}.")
            except Exception as e:
                logger.warning(f"ChromaDB not available ({e}). Using in-memory vector store fallback.")
                self._use_fallback = True
        return self._collection

    def add_facts(self, items: List[Dict[str, Any]]) -> List[str]:
        """
        Upserts fact embeddings into the vector store.
        Each item is: {"fact_id": str, "embedding": List[float], "metadata": dict, "document": str}
        """
        if not items:
            return []

        ids = [item["fact_id"] for item in items]
        embeddings = [item["embedding"] for item in items]
        metadatas = [self._sanitize_metadata(item.get("metadata", {})) for item in items]
        documents = [item.get("document", "") for item in items]

        collection = self._get_collection()
        if collection is not None and not self._use_fallback:
            try:
                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                return ids
            except Exception as e:
                logger.error(f"ChromaDB upsert failed: {e}")

        # In-memory fallback
        for item in items:
            self._fallback_store[item["fact_id"]] = {
                "fact_id": item["fact_id"],
                "embedding": item["embedding"],
                "metadata": self._sanitize_metadata(item.get("metadata", {})),
                "document": item.get("document", "")
            }
        return ids

    def query_similar_facts(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries top-K semantically similar facts by embedding.
        Returns list of {"fact_id": str, "similarity": float, "metadata": dict, "document": str}.
        """
        collection = self._get_collection()
        if collection is not None and not self._use_fallback:
            try:
                count = collection.count()
                if count == 0:
                    return []

                actual_n = min(n_results, count)
                kwargs: Dict[str, Any] = {
                    "query_embeddings": [query_embedding],
                    "n_results": actual_n
                }
                if filter_dict:
                    kwargs["where"] = filter_dict

                results = collection.query(**kwargs)
                formatted = []
                if results and results["ids"] and len(results["ids"][0]) > 0:
                    ids = results["ids"][0]
                    distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
                    metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
                    documents = results["documents"][0] if results.get("documents") else [""] * len(ids)

                    for fid, dist, meta, doc in zip(ids, distances, metadatas, documents):
                        # Cosine distance to similarity (similarity in [0, 1])
                        sim = max(0.0, min(1.0, 1.0 - (dist / 2.0)))
                        formatted.append({
                            "fact_id": fid,
                            "similarity": round(sim, 4),
                            "metadata": meta,
                            "document": doc
                        })
                return formatted
            except Exception as e:
                logger.error(f"ChromaDB query failed: {e}")

        # In-memory cosine search fallback
        return self._in_memory_query(query_embedding, n_results, filter_dict)

    def _in_memory_query(
        self,
        query_embedding: List[float],
        n_results: int,
        filter_dict: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        candidates = []
        for fid, data in self._fallback_store.items():
            if filter_dict:
                match = True
                for k, v in filter_dict.items():
                    if data["metadata"].get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            # Dot product for normalized vectors
            emb = data["embedding"]
            sim = sum(a * b for a, b in zip(query_embedding, emb))
            sim = max(0.0, min(1.0, (sim + 1.0) / 2.0))
            candidates.append({
                "fact_id": fid,
                "similarity": round(sim, 4),
                "metadata": data["metadata"],
                "document": data["document"]
            })

        candidates.sort(key=lambda x: x["similarity"], reverse=True)
        return candidates[:n_results]

    def delete_by_document_id(self, document_id: str) -> None:
        collection = self._get_collection()
        if collection is not None and not self._use_fallback:
            try:
                collection.delete(where={"document_id": document_id})
            except Exception as e:
                logger.error(f"ChromaDB delete by doc failed: {e}")

        to_del = [fid for fid, d in self._fallback_store.items() if d["metadata"].get("document_id") == document_id]
        for fid in to_del:
            del self._fallback_store[fid]

    def delete_by_fact_id(self, fact_id: str) -> None:
        collection = self._get_collection()
        if collection is not None and not self._use_fallback:
            try:
                collection.delete(ids=[fact_id])
            except Exception as e:
                logger.error(f"ChromaDB delete by fact ID failed: {e}")

        if fact_id in self._fallback_store:
            del self._fallback_store[fact_id]

    def count(self) -> int:
        collection = self._get_collection()
        if collection is not None and not self._use_fallback:
            try:
                return collection.count()
            except Exception:
                pass
        return len(self._fallback_store)

    def reset(self) -> None:
        """Clears all vectors from the Chroma collection and fallback store."""
        if self._collection is not None and not self._use_fallback:
            try:
                if self._client is not None:
                    self._client.delete_collection(self.collection_name)
                    self._collection = self._client.get_or_create_collection(
                        name=self.collection_name,
                        metadata={"hnsw:space": "cosine"}
                    )
            except Exception as e:
                logger.warning(f"Error resetting ChromaDB collection: {e}")
                self._collection = None
        self._fallback_store.clear()

    def _sanitize_metadata(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures metadata values are valid primitives for ChromaDB (str, int, float, bool)."""
        clean = {}
        for k, v in meta.items():
            if v is None:
                clean[k] = ""
            elif isinstance(v, (str, int, float, bool)):
                clean[k] = v
            else:
                clean[k] = str(v)
        return clean


# Global singleton instance
vector_store = ChromaVectorStore()

