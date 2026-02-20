from datetime import date

from app.evaluation import evaluate_report
from app.models.schemas import InvestmentMemo, MemoSection, RetrievedEvidence


def _section(score: float) -> MemoSection:
    return MemoSection(
        summary="s",
        score=score,
        evidence=[RetrievedEvidence(source="x", score=0.8, excerpt="e", metadata={})],
    )


def test_evaluator_outputs_ranges() -> None:
    report = InvestmentMemo(
        startup_name="X",
        generated_on=date.today(),
        market=_section(6.0),
        competition=_section(5.5),
        traction=_section(6.2),
        business_model=_section(5.8),
        risk_assessment=_section(4.7),
        key_risks=["r"],
        recommendation="Proceed",
    )

    out = evaluate_report(report)
    assert 0.0 <= out.retrieval_relevance <= 10.0
    assert 0.0 <= out.citation_coverage <= 1.0
    assert 0.0 <= out.consistency_score <= 10.0
    assert 0.0 <= out.hallucination_risk <= 1.0
    assert out.judge_verdict in {"strong", "acceptable", "needs_review"}
