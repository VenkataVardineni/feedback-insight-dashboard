## Feedback Insight Dashboard – Architecture

### Goal

A product manager can drop a feedback dump (≈50 short lines) and immediately see high-level sentiment to guide roadmap planning.

### Components

- **Frontend (`frontend/`)**: React + TypeScript dashboard UI.
  - Input: multi-line textarea (one comment per line)
  - Output: per-line table (label + score) and a sentiment distribution chart
  - Calls the backend API endpoints below.

- **Backend (`backend/`)**: FastAPI service.
  - `POST /feedback/analyze-batch`: batch sentiment scoring and aggregate stats
  - `GET /feedback/stats`: aggregated stats over recent requests (in-memory rolling window)

- **Sentiment provider (SmartReview)**:
  - If `SMARTREVIEW_URL` is set, backend calls SmartReview over HTTP (`POST /sentiment/analyze`).
  - If not set / unreachable, backend uses a small built-in heuristic so the app is runnable end-to-end.

### Data flow

1. PM pastes feedback lines in the UI and clicks **Analyze**.
2. Frontend sends JSON:
   - `{ "feedback": ["line1", "line2", ...] }`
3. Backend scores each item via SmartReview (or fallback), returns:
   - per-item results (text, label, score)
   - aggregate stats (positive/negative/neutral %, avg score)
4. Frontend renders KPIs, table, and chart.

### Storage model

- **Request history**: rolling in-memory deque (default window = 50 requests) used by `GET /feedback/stats`.
  - This is intentionally simple for MVP. Swap to SQLite/Redis later if you need persistence across restarts.

### Deployment (Docker Compose)

- `frontend` (Nginx): serves the built SPA and reverse-proxies `/feedback/*` and `/health` to `backend`.
- `backend` (Uvicorn): serves the API.

