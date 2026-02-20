# Trade-offs and Engineering Decisions

## Retrieval

- Decision: Hybrid retrieval (vector + BM25)
- Benefit: Better precision on proper nouns and finance terms
- Cost: More logic, slightly higher compute than vector-only

## Embeddings

- Decision: Prefer BGE model, fallback to TF-IDF
- Benefit: Works in restricted or low-bandwidth environments
- Cost: TF-IDF semantic quality is weaker than transformer embeddings

## Vector Database

- Decision: Prefer Qdrant, fallback to in-memory vector index
- Benefit: Local reliability and cloud path with same interface
- Cost: In-memory mode lacks persistence and advanced indexing

## Evaluation

- Decision: Lightweight judge metrics (coverage/consistency/risk)
- Benefit: Fast, cheap runtime quality signal
- Cost: Not a full benchmark replacement for human-labeled evaluation

## Deployment

- Decision: Docker + Render Blueprint
- Benefit: Simple path from local to cloud
- Cost: Limited autoscaling/custom infra compared to full Kubernetes setup
