from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class AnalyzeStartupRequest(BaseModel):
    startup_name: str = Field(min_length=2, max_length=120)
    website_url: HttpUrl
    max_news_articles: int = Field(default=5, ge=0, le=20)
    public_pdf_urls: List[HttpUrl] = Field(default_factory=list)


class SourceDocument(BaseModel):
    source: str
    type: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetrievedEvidence(BaseModel):
    source: str
    score: float
    excerpt: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoSection(BaseModel):
    summary: str
    score: float = Field(ge=0.0, le=10.0)
    evidence: List[RetrievedEvidence] = Field(default_factory=list)


class InvestmentMemo(BaseModel):
    startup_name: str
    generated_on: date
    market: MemoSection
    competition: MemoSection
    traction: MemoSection
    business_model: MemoSection
    risk_assessment: MemoSection
    key_risks: List[str]
    recommendation: str


class EvaluationMetrics(BaseModel):
    retrieval_relevance: float = Field(ge=0.0, le=10.0)
    citation_coverage: float = Field(ge=0.0, le=1.0)
    consistency_score: float = Field(ge=0.0, le=10.0)
    hallucination_risk: float = Field(ge=0.0, le=1.0)
    judge_verdict: str


class RunMetrics(BaseModel):
    latency_ms: int = Field(ge=0)
    input_characters: int = Field(ge=0)
    estimated_input_tokens: int = Field(ge=0)
    estimated_cost_usd: float = Field(ge=0.0)


class AnalyzeStartupResponse(BaseModel):
    status: str
    report: InvestmentMemo
    evaluation: EvaluationMetrics
    metrics: RunMetrics
    sources_indexed: int
    notes: Optional[str] = None
