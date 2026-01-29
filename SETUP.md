## Setup (Local + Docker)

This repo contains:

- `backend/`: FastAPI API for batch sentiment analysis
- `frontend/`: React + TypeScript dashboard UI

---

## Option A: Run with Docker (recommended)

### Prereqs

- Docker Desktop (or Docker Engine) with Compose v2

### Start

```bash
docker compose up --build
```

### Open

- Frontend UI: `http://localhost:5173`
- Backend API: `http://localhost:8000`
  - Health: `GET /health`

### Stop

```bash
docker compose down
```

---

## Option B: Run locally (no Docker)

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Backend health check:

```bash
curl -s http://localhost:8000/health
```

### Frontend (React + TS)

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:5173`

---

## SmartReview Sentiment Service (optional)

The backend can call SmartReview over HTTP for scoring. If configured, it will send:

- `POST {SMARTREVIEW_URL}/sentiment/analyze`
  - body: `{ "text": "..." }`
  - expected response: `{ "score": 0.7 }` or `{ "score": 0.7, "label": "positive" }`

### Configure

Set the environment variable on the backend:

- `SMARTREVIEW_URL` (example: `http://localhost:9000`)

With Docker Compose, you can set it in `docker-compose.yml` under `backend.environment`.

---

## Notes

- The app works end-to-end even without SmartReview, using a lightweight built-in heuristic in the backend.
- Request-level stats are stored in memory (rolling window) for the `/feedback/stats` endpoint.

