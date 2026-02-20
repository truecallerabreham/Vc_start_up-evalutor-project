from datetime import date

from app.models.schemas import InvestmentMemo, MemoSection, RetrievedEvidence
from app.retrieval.search import HybridHit


def _to_evidence(hits: list[HybridHit], max_items: int = 3) -> list[RetrievedEvidence]:
    out: list[RetrievedEvidence] = []
    for hit in hits[:max_items]:
        out.append(
            RetrievedEvidence(
                source=hit.source,
                score=round(float(hit.score), 4),
                excerpt=hit.content[:500],
                metadata=hit.metadata,
            )
        )
    return out


def _score_from_hits(hits: list[HybridHit]) -> float:
    if not hits:
        return 3.0
    avg = sum(max(0.0, h.score) for h in hits[:5]) / min(len(hits), 5)
    return max(1.0, min(10.0, round(3.0 + avg, 2)))


def build_single_agent_memo(startup_name: str, hits: list[HybridHit]) -> InvestmentMemo:
    evidence = _to_evidence(hits)

    market = MemoSection(
        summary="The startup appears positioned in an active AI market segment based on website/news signals.",
        score=_score_from_hits(hits),
        evidence=evidence,
    )

    traction = MemoSection(
        summary="Public references indicate early traction signals, but deeper KPI validation is needed.",
        score=max(1.0, market.score - 0.7),
        evidence=evidence,
    )

    business_model = MemoSection(
        summary="Business model indicators are present in public materials; confirm pricing, GTM, and retention data.",
        score=max(1.0, market.score - 0.4),
        evidence=evidence,
    )

    risk_flags = [
        "Limited verified financial metrics from public sources.",
        "Potential over-reliance on marketing claims without independent validation.",
        "Competitive pressure from adjacent AI platforms.",
    ]

    recommendation = "Proceed to partner-level diligence call" if market.score >= 5.5 else "Watchlist pending more traction evidence"

    return InvestmentMemo(
        startup_name=startup_name,
        generated_on=date.today(),
        market=market,
        traction=traction,
        business_model=business_model,
        key_risks=risk_flags,
        recommendation=recommendation,
    )
