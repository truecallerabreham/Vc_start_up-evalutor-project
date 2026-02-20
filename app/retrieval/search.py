from dataclasses import dataclass

from rank_bm25 import BM25Okapi


@dataclass
class HybridHit:
    source: str
    score: float
    content: str
    metadata: dict


class HybridRetriever:
    def __init__(self, docs: list[dict]) -> None:
        self.docs = docs
        tokenized = [d["content"].lower().split() for d in docs]
        self.bm25 = BM25Okapi(tokenized) if tokenized else None

    def keyword_scores(self, query: str) -> list[float]:
        if not self.bm25:
            return [0.0] * len(self.docs)
        return self.bm25.get_scores(query.lower().split()).tolist()


def _normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    v_min = min(values)
    v_max = max(values)
    if v_max == v_min:
        return [1.0 for _ in values]
    return [(v - v_min) / (v_max - v_min) for v in values]


def hybrid_search(
    vector_hits,
    docs: list[dict],
    query: str,
    top_k: int = 8,
    metadata_filter: dict | None = None,
    vector_weight: float = 0.7,
    keyword_weight: float = 0.3,
) -> list[HybridHit]:
    retriever = HybridRetriever(docs)
    bm25_scores = retriever.keyword_scores(query)
    normalized_bm25 = _normalize([float(s) for s in bm25_scores])

    id_to_vector_score: dict[tuple[str, str], float] = {}
    vector_raw_scores: list[float] = []

    for hit in vector_hits:
        payload = hit.payload or {}
        key = (payload.get("source", "unknown"), payload.get("content", ""))
        raw_score = float(hit.score)
        id_to_vector_score[key] = raw_score
        vector_raw_scores.append(raw_score)

    vector_norm_map: dict[tuple[str, str], float] = {}
    vector_norm_values = _normalize(vector_raw_scores)
    for i, hit in enumerate(vector_hits):
        payload = hit.payload or {}
        key = (payload.get("source", "unknown"), payload.get("content", ""))
        vector_norm_map[key] = vector_norm_values[i] if i < len(vector_norm_values) else 0.0

    combined: list[HybridHit] = []
    for idx, doc in enumerate(docs):
        metadata = doc.get("metadata", {})
        if metadata_filter:
            is_match = True
            for key, value in metadata_filter.items():
                if metadata.get(key) != value:
                    is_match = False
                    break
            if not is_match:
                continue

        key = (doc.get("source", "unknown"), doc.get("content", ""))
        vector_component = vector_norm_map.get(key, 0.0)
        keyword_component = normalized_bm25[idx] if idx < len(normalized_bm25) else 0.0
        score = (vector_weight * vector_component) + (keyword_weight * keyword_component)

        if score <= 0:
            continue

        combined.append(
            HybridHit(
                source=doc.get("source", "unknown"),
                score=score,
                content=doc.get("content", ""),
                metadata=metadata,
            )
        )

    combined.sort(key=lambda x: x.score, reverse=True)
    return combined[:top_k]
