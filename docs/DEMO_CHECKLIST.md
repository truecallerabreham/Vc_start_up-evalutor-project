# Demo Checklist

## 1. Startup and Health

- Run server: `python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload`
- Open `http://127.0.0.1:8000/status`
- Confirm `phase` is `phase_3`

## 2. UI Walkthrough

- Open `http://127.0.0.1:8000/ui`
- Enter startup name and URL
- Click `Run Analysis`
- Show:
  - Recommendation
  - Section-level scores
  - Key risks
  - Verdict, latency, estimated cost

## 3. Explain System

- Ingestion -> chunking -> embeddings -> hybrid retrieval -> agents -> synthesis -> evaluation
- Why citation coverage and hallucination risk matter for investor workflows

## 4. Close

- Mention Docker + Render deployability
- Mention Qdrant cloud compatibility
- Mention extension path: real LLM provider integration and benchmark dataset
