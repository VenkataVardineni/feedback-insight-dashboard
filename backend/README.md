## Backend (FastAPI)

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Env vars

- **`SMARTREVIEW_URL`**: If set (example `http://smartreview:9000`), backend will call `POST /sentiment/analyze` on that service.
- **`STATS_WINDOW`**: Max number of recent requests kept in memory (default `50`).
- **`CORS_ALLOW_ORIGIN`**: CORS allow origin (default `*`).

