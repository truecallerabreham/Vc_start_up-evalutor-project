from app.models.schemas import EvaluationMetrics, InvestmentMemo


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def evaluate_report(report: InvestmentMemo) -> EvaluationMetrics:
    all_sections = [
        report.market,
        report.competition,
        report.traction,
        report.business_model,
        report.risk_assessment,
    ]

    section_scores = [float(section.score) for section in all_sections]
    retrieval_relevance = max(0.0, min(10.0, round(_mean(section_scores), 2)))

    evidence_counts = [len(section.evidence) for section in all_sections]
    sections_with_evidence = sum(1 for n in evidence_counts if n > 0)
    citation_coverage = round(sections_with_evidence / len(all_sections), 2)

    spread = (max(section_scores) - min(section_scores)) if section_scores else 10.0
    consistency_score = max(0.0, min(10.0, round(10.0 - (spread * 0.9), 2)))

    hallucination_risk = round(max(0.0, min(1.0, 1.0 - citation_coverage + (0.08 if retrieval_relevance < 5 else 0.0))), 2)

    if hallucination_risk <= 0.2 and retrieval_relevance >= 6.0:
        verdict = "strong"
    elif hallucination_risk <= 0.45 and retrieval_relevance >= 4.5:
        verdict = "acceptable"
    else:
        verdict = "needs_review"

    return EvaluationMetrics(
        retrieval_relevance=retrieval_relevance,
        citation_coverage=citation_coverage,
        consistency_score=consistency_score,
        hallucination_risk=hallucination_risk,
        judge_verdict=verdict,
    )
