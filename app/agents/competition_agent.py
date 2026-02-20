from app.models.schemas import MemoSection, RetrievedEvidence
from app.retrieval.search import HybridHit


def _score(hits: list[HybridHit]) -> float:
    if not hits:
        return 2.8
    avg = sum(h.score for h in hits[:5]) / min(len(hits), 5)
    return max(1.0, min(10.0, round(3.8 + (avg * 5.8), 2)))


def _evidence(hits: list[HybridHit], limit: int = 3) -> list[RetrievedEvidence]:
    return [
        RetrievedEvidence(
            source=h.source,
            score=round(float(h.score), 4),
            excerpt=h.content[:500],
            metadata=h.metadata,
        )
        for h in hits[:limit]
    ]


def run_competition_agent(startup_name: str, hits: list[HybridHit]) -> MemoSection:
    summary = (
        f"{startup_name} has identifiable competitive pressure in adjacent AI categories. "
        "Differentiate on product moats, distribution, and execution speed."
    )
    return MemoSection(summary=summary, score=_score(hits), evidence=_evidence(hits))
