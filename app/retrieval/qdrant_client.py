from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import uuid4

import numpy as np

from app.models.schemas import SourceDocument


@dataclass
class LocalHit:
    score: float
    payload: dict


class VentureQdrant:
    """
    Uses qdrant-client when installed, otherwise falls back to an in-memory vector store.
    """

    def __init__(
        self,
        collection_name: str,
        vector_size: int,
        qdrant_url: str = "",
        qdrant_api_key: str = "",
        local_path: str = ":memory:",
    ) -> None:
        self.collection_name = collection_name
        self.vector_size = vector_size
        self._backend = "local"
        self._local_points: list[dict] = []

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models

            self._models = models
            if qdrant_url:
                self.client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
            else:
                self.client = QdrantClient(location=local_path)
            self._ensure_collection(vector_size)
            self._backend = "qdrant"
        except Exception:
            self.client = None
            self._models = None

    def _ensure_collection(self, vector_size: int) -> None:
        if self.client is None:
            return

        collections = self.client.get_collections().collections
        existing = {c.name for c in collections}
        if self.collection_name not in existing:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=self._models.VectorParams(size=vector_size, distance=self._models.Distance.COSINE),
            )

    def upsert_documents(self, docs: List[SourceDocument], vectors: List[List[float]]) -> int:
        if self._backend == "qdrant" and self.client is not None:
            points: list = []
            for doc, vec in zip(docs, vectors):
                payload = {
                    "source": doc.source,
                    "type": doc.type,
                    "content": doc.content,
                    "metadata": doc.metadata,
                }
                points.append(self._models.PointStruct(id=str(uuid4()), vector=vec, payload=payload))

            self.client.upsert(collection_name=self.collection_name, points=points)
            return len(points)

        for doc, vec in zip(docs, vectors):
            self._local_points.append(
                {
                    "id": str(uuid4()),
                    "vector": np.array(vec, dtype=np.float32),
                    "payload": {
                        "source": doc.source,
                        "type": doc.type,
                        "content": doc.content,
                        "metadata": doc.metadata,
                    },
                }
            )
        return len(vectors)

    def search(self, query_vector: List[float], top_k: int = 8, metadata_filter: Optional[Dict[str, Any]] = None):
        if self._backend == "qdrant" and self.client is not None:
            query_filter = None
            if metadata_filter:
                conditions = []
                for key, value in metadata_filter.items():
                    conditions.append(self._models.FieldCondition(key=f"metadata.{key}", match=self._models.MatchValue(value=value)))
                query_filter = self._models.Filter(must=conditions)

            return self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True,
            )

        q = np.array(query_vector, dtype=np.float32)
        q_norm = float(np.linalg.norm(q)) or 1.0
        hits: list[LocalHit] = []

        for point in self._local_points:
            payload = point["payload"]
            if metadata_filter:
                match = True
                metadata = payload.get("metadata", {})
                for key, value in metadata_filter.items():
                    if metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            v = point["vector"]
            v_norm = float(np.linalg.norm(v)) or 1.0
            score = float(np.dot(q, v) / (q_norm * v_norm))
            hits.append(LocalHit(score=score, payload=payload))

        hits.sort(key=lambda x: x.score, reverse=True)
        return hits[:top_k]
