from time import perf_counter

from app.agents import (
    run_competition_agent,
    run_market_agent,
    run_risk_agent,
    run_traction_agent,
    synthesize_investment_memo,
)
from app.config.settings import get_settings
from app.embeddings.embedder import BGEEmbedder
from app.evaluation import evaluate_report
from app.ingestion.news_scraper import scrape_news
from app.ingestion.pdf_parser import parse_public_pdf
from app.ingestion.web_scraper import scrape_website
from app.models.schemas import AnalyzeStartupRequest, AnalyzeStartupResponse, RunMetrics
from app.retrieval.chunker import chunk_documents
from app.retrieval.qdrant_client import VentureQdrant
from app.retrieval.search import hybrid_search
from app.utils.logger import setup_logger


settings = get_settings()
logger = setup_logger("venturelens.pipeline")


def _estimate_tokens(char_count: int) -> int:
    # Lightweight heuristic for English text in absence of provider tokenizers.
    return max(1, int(char_count / 4))


def _estimate_cost_usd(input_tokens: int, price_per_million: float = 0.15) -> float:
    return round((input_tokens / 1_000_000) * price_per_million, 6)


async def run_analysis(payload: AnalyzeStartupRequest) -> AnalyzeStartupResponse:
    start_time = perf_counter()

    docs = []

    website_docs = await scrape_website(str(payload.website_url))
    docs.extend(website_docs)

    news_docs = await scrape_news(payload.startup_name, payload.max_news_articles)
    docs.extend(news_docs)

    for pdf_url in payload.public_pdf_urls:
        pdf_docs = await parse_public_pdf(str(pdf_url))
        docs.extend(pdf_docs)

    chunked_docs = chunk_documents(docs, max_chunk_size=settings.max_chunk_size, overlap=settings.chunk_overlap)
    if not chunked_docs:
        raise ValueError("No documents extracted from provided sources.")

    embedder = BGEEmbedder(settings.embedding_model)
    texts = [d.content for d in chunked_docs]
    vectors = embedder.embed_texts(texts)
    vector_size = len(vectors[0])

    qdrant = VentureQdrant(
        collection_name=settings.qdrant_collection,
        vector_size=vector_size,
        qdrant_url=settings.qdrant_url,
        qdrant_api_key=settings.qdrant_api_key,
        local_path=settings.qdrant_local_path,
    )

    indexed_count = qdrant.upsert_documents(chunked_docs, vectors)

    docs_index = [
        {
            "source": d.source,
            "content": d.content,
            "metadata": d.metadata,
            "type": d.type,
        }
        for d in chunked_docs
    ]

    def retrieve(query: str, metadata_filter: dict | None = None, top_k: int = 8):
        q_vector = embedder.embed_query(query)
        vector_hits = qdrant.search(query_vector=q_vector, top_k=max(top_k * 2, 12), metadata_filter=metadata_filter)
        return hybrid_search(
            vector_hits=vector_hits,
            docs=docs_index,
            query=query,
            top_k=top_k,
            metadata_filter=metadata_filter,
        )

    market_hits = retrieve(f"{payload.startup_name} ai market trends demand segments", top_k=8)
    competition_hits = retrieve(f"{payload.startup_name} competitors alternatives differentiation moat", top_k=8)
    traction_hits = retrieve(f"{payload.startup_name} users customers funding partnerships growth", top_k=8)
    risk_hits = retrieve(f"{payload.startup_name} risk legal compliance security reliability", top_k=8)

    market = run_market_agent(payload.startup_name, market_hits)
    competition = run_competition_agent(payload.startup_name, competition_hits)
    traction = run_traction_agent(payload.startup_name, traction_hits)
    risk = run_risk_agent(payload.startup_name, risk_hits)

    report = synthesize_investment_memo(
        startup_name=payload.startup_name,
        market=market,
        competition=competition,
        traction=traction,
        risk=risk,
    )

    evaluation = evaluate_report(report)

    input_characters = sum(len(d.content) for d in chunked_docs)
    estimated_input_tokens = _estimate_tokens(input_characters)
    metrics = RunMetrics(
        latency_ms=int((perf_counter() - start_time) * 1000),
        input_characters=input_characters,
        estimated_input_tokens=estimated_input_tokens,
        estimated_cost_usd=_estimate_cost_usd(estimated_input_tokens),
    )

    logger.info(
        "analysis_complete startup=%s sources=%s latency_ms=%s verdict=%s hallucination_risk=%.2f tokens=%s cost_usd=%.6f",
        payload.startup_name,
        indexed_count,
        metrics.latency_ms,
        evaluation.judge_verdict,
        evaluation.hallucination_risk,
        metrics.estimated_input_tokens,
        metrics.estimated_cost_usd,
    )

    return AnalyzeStartupResponse(
        status="ok",
        report=report,
        evaluation=evaluation,
        metrics=metrics,
        sources_indexed=indexed_count,
        notes="Phase 3 pipeline executed: evaluation + metrics logging enabled.",
    )


# Backward-compatible alias for older imports.
run_phase1_analysis = run_analysis
