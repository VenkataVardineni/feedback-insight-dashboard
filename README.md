## Feedback Insight Dashboard

A web dashboard that helps product teams quickly understand the **overall sentiment** of a batch of user feedback.

The core UX is intentionally simple:

- Paste a dump of feedback (one comment per line)
- Click **Analyze**
- Immediately see:
  - overall **positive / neutral / negative** percentages
  - a per-comment table (sentiment label + score)
  - a compact “mood distribution” chart

---

## Tech stack

- **Frontend**: React + TypeScript (Vite)
- **Backend**: FastAPI (Python) + Uvicorn
- **Sentiment provider**:
  - **SmartReview Sentiment Service** (optional, via HTTP)
  - a **built-in fallback heuristic** so the app runs end-to-end even without SmartReview
- **Deployment**: Docker Compose
  - Frontend is served with **Nginx** (static SPA) and reverse-proxies API calls to the backend

---

## Project structure

- `frontend/`
  - React page with textarea input, Analyze button, results table, and chart
  - Calls the backend endpoint `POST /feedback/analyze-batch`
- `backend/`
  - FastAPI service implementing sentiment analysis endpoints + in-memory request stats
- `docs/architecture.md`
  - Architecture overview and data flow
- `SETUP.md`
  - Step-by-step setup instructions (Docker + local)

---

## How it works (end-to-end)

1. The PM pastes feedback lines into the UI (one line = one comment).
2. Frontend sends:
   - `POST /feedback/analyze-batch`
   - body: `{ "feedback": ["line1", "line2", ...] }`
3. Backend scores each line:
   - If `SMARTREVIEW_URL` is set, calls SmartReview:
     - `POST {SMARTREVIEW_URL}/sentiment/analyze` with `{ "text": "..." }`
   - Otherwise, uses a small built-in heuristic (so the app still works).
4. Backend returns:
   - per-item results (text, label, score)
   - aggregate stats (positive/neutral/negative %, average score)
5. Frontend renders KPIs, table, and mood chart.

---

## API reference

### `GET /health`

Returns:

- `{ "status": "ok" }`

### `POST /feedback/analyze-batch`

Request:

- body:
  - `{ "feedback": ["text1", "text2", "..."] }`

Response (shape):

- `items[]`: `{ text, score, label }`
  - `score`: float in `[-1, 1]` (higher = more positive)
  - `label`: `"positive" | "neutral" | "negative"`
- `stats`: `{ total, positive_pct, neutral_pct, negative_pct, avg_score }`

### `GET /feedback/stats?last_n=20`

Aggregates stats over the last N requests stored in memory (rolling window).

Response includes:

- total items analyzed across the considered requests
- label counts and percentages
- average score across all considered items

---

## Run it

See `SETUP.md`.

---

## Docs

- `docs/architecture.md`

