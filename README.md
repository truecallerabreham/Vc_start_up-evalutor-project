# VentureLens AI

Open-weight startup due diligence assistant for AI investing.

## Phase Status

- `Phase 0`: complete (project structure + configs)
- `Phase 1`: complete (website/news/PDF ingestion + indexing)
- `Phase 2`: complete (hybrid retrieval + multi-agent report synthesis)
- `Phase 3`: complete (evaluation + latency/token/cost metrics)
- `Phase 4`: complete (Docker + Render deployment setup)

## Local Run

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
python -m uvicorn app.api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open:
- `http://127.0.0.1:8000/ui`
- `http://127.0.0.1:8000/status`

## Docker Run

```bash
docker build -f docker/Dockerfile -t venturelens-ai .
docker run --rm -p 8000:8000 --env PORT=8000 venturelens-ai
```

## Render Deployment

1. Push this repository to GitHub.
2. In Render: `New +` -> `Blueprint`.
3. Select your repo (Render reads `render.yaml`).
4. Set secret env vars in Render dashboard:
   - `QDRANT_URL`
   - `QDRANT_API_KEY`
5. Deploy and verify:
   - `/status` returns `{"status":"ok", ...}`
   - `/ui` loads the application UI.

## API Endpoints

- `GET /status`: health check
- `GET /ui`: web UI
- `POST /analyze_startup`: due diligence report generation

## Notes

- For local troubleshooting, keep `REQUEST_VERIFY_SSL=false`.
- For cloud deployment, use `REQUEST_VERIFY_SSL=true`.
