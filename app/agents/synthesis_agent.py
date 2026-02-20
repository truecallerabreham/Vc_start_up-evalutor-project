from datetime import date

from app.models.schemas import InvestmentMemo, MemoSection


def _business_model_from_sections(market: MemoSection, traction: MemoSection) -> MemoSection:
    score = max(1.0, min(10.0, round((market.score * 0.45) + (traction.score * 0.55), 2)))
    summary = "Revenue model appears plausible but requires pricing, retention, and unit economics validation."
    evidence = (market.evidence + traction.evidence)[:3]
    return MemoSection(summary=summary, score=score, evidence=evidence)


def _build_key_risks(competition: MemoSection, risk: MemoSection) -> list[str]:
    risks = [
        "Limited verified financial disclosure from public sources.",
        "Execution risk against fast-moving AI competitors.",
        "Potential compliance and model reliability risk in regulated contexts.",
    ]
    if competition.score >= 7.5:
        risks.append("High market heat could compress differentiation unless moat is defensible.")
    if risk.score < 5.0:
        risks.append("Insufficient public data to confidently score risk profile.")
    return risks


def synthesize_investment_memo(
    startup_name: str,
    market: MemoSection,
    competition: MemoSection,
    traction: MemoSection,
    risk: MemoSection,
) -> InvestmentMemo:
    business_model = _business_model_from_sections(market, traction)
    key_risks = _build_key_risks(competition, risk)

    weighted_score = (
        (market.score * 0.25)
        + (competition.score * 0.15)
        + (traction.score * 0.30)
        + (business_model.score * 0.20)
        + (max(1.0, 10.0 - risk.score) * 0.10)
    )

    recommendation = "Proceed to IC deep-dive" if weighted_score >= 6.2 else "Watchlist pending stronger proof points"

    return InvestmentMemo(
        startup_name=startup_name,
        generated_on=date.today(),
        market=market,
        competition=competition,
        traction=traction,
        business_model=business_model,
        risk_assessment=risk,
        key_risks=key_risks,
        recommendation=recommendation,
    )
