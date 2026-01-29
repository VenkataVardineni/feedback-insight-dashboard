## Feedback Insight Dashboard

Visual dashboard to analyze sentiment of batches of feedback.

### What you get

- Paste ~50 feedback lines
- Click **Analyze**
- See:
  - overall positive/neutral/negative percentages
  - a table of each comment with sentiment + score
  - a small chart summarizing mood distribution

### Run with Docker

```bash
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000` (health: `/health`)

### Run locally (no Docker)

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

### API

- `POST /feedback/analyze-batch`
  - body: `{ "feedback": ["text1", "text2"] }`
  - returns: per-item results + aggregate stats
- `GET /feedback/stats?last_n=20`
  - returns: aggregated stats over last N requests stored in memory

### SmartReview integration

If you have SmartReview Sentiment Service running, set:

- `SMARTREVIEW_URL` (example `http://smartreview:9000`)

Backend will call `POST /sentiment/analyze` on SmartReview. If not set/unreachable, a simple local heuristic is used so the app still runs.

### Docs

See `docs/architecture.md`.

