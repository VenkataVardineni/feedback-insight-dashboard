from __future__ import annotations

import os
import time
from collections import Counter, deque
from typing import Deque, List, Literal, Optional

from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .sentiment_client import SentimentResult, analyze_sentiment


SentimentLabel = Literal["positive", "negative", "neutral"]


class AnalyzeBatchRequest(BaseModel):
    feedback: List[str] = Field(..., min_length=1, description="List of feedback strings")


class FeedbackItemResult(BaseModel):
    text: str
    score: float
    label: SentimentLabel


class AggregateStats(BaseModel):
    total: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    avg_score: float


class AnalyzeBatchResponse(BaseModel):
    items: List[FeedbackItemResult]
    stats: AggregateStats


class StatsResponse(BaseModel):
    window_size: int
    requests_considered: int
    total_items: int
    label_counts: dict[SentimentLabel, int]
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    avg_score: float
    last_request_at_epoch_s: Optional[float] = None


class _StoredRequest(BaseModel):
    created_at_epoch_s: float
    scores: List[float]
    labels: List[SentimentLabel]


def _pct(n: int, d: int) -> float:
    return round((100.0 * n / d), 2) if d else 0.0


def _avg(nums: List[float]) -> float:
    return round((sum(nums) / len(nums)), 4) if nums else 0.0


STATS_WINDOW = int(os.getenv("STATS_WINDOW", "50"))
_requests: Deque[_StoredRequest] = deque(maxlen=STATS_WINDOW)

app = FastAPI(title="Feedback Insight Dashboard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ALLOW_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/feedback/analyze-batch", response_model=AnalyzeBatchResponse)
async def analyze_batch(req: AnalyzeBatchRequest) -> AnalyzeBatchResponse:
    results: List[SentimentResult] = []
    for text in req.feedback:
        results.append(await analyze_sentiment(text))

    items = [
        FeedbackItemResult(text=text, score=r.score, label=r.label) for text, r in zip(req.feedback, results)
    ]

    labels = [i.label for i in items]
    scores = [i.score for i in items]
    counts = Counter(labels)
    total = len(items)

    stats = AggregateStats(
        total=total,
        positive_pct=_pct(counts.get("positive", 0), total),
        negative_pct=_pct(counts.get("negative", 0), total),
        neutral_pct=_pct(counts.get("neutral", 0), total),
        avg_score=_avg(scores),
    )

    _requests.append(
        _StoredRequest(
            created_at_epoch_s=time.time(),
            scores=scores,
            labels=labels,  # type: ignore[arg-type]
        )
    )

    return AnalyzeBatchResponse(items=items, stats=stats)


@app.get("/feedback/stats", response_model=StatsResponse)
def stats(last_n: int = Query(default=20, ge=1, le=500)) -> StatsResponse:
    reqs = list(_requests)[-last_n:]
    all_scores: List[float] = []
    all_labels: List[SentimentLabel] = []
    last_ts: Optional[float] = None

    for r in reqs:
        all_scores.extend(r.scores)
        all_labels.extend(r.labels)
        last_ts = r.created_at_epoch_s

    total_items = len(all_labels)
    counts = Counter(all_labels)

    return StatsResponse(
        window_size=STATS_WINDOW,
        requests_considered=len(reqs),
        total_items=total_items,
        label_counts={
            "positive": int(counts.get("positive", 0)),
            "negative": int(counts.get("negative", 0)),
            "neutral": int(counts.get("neutral", 0)),
        },
        positive_pct=_pct(counts.get("positive", 0), total_items),
        negative_pct=_pct(counts.get("negative", 0), total_items),
        neutral_pct=_pct(counts.get("neutral", 0), total_items),
        avg_score=_avg(all_scores),
        last_request_at_epoch_s=last_ts,
    )

