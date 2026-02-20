from app.models.schemas import MemoSection, RetrievedEvidence
from app.retrieval.search import HybridHit


def _score(hits: list[HybridHit]) -> float:
    if not hits:
        return 4.0
    avg = sum(h.score for h in hits[:5]) / min(len(hits), 5)
    # Higher evidence on risk terms means stronger risk visibility, not necessarily safer business.
    return max(1.0, min(10.0, round(4.0 + (avg * 4.5), 2)))


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


def run_risk_agent(startup_name: str, hits: list[HybridHit]) -> MemoSection:
    summary = (
        f"{startup_name} requires diligence on compliance, model reliability, and dependency risks. "
        "Confirm legal exposure and operational resilience before committing capital."
    )
    return MemoSection(summary=summary, score=_score(hits), evidence=_evidence(hits))
