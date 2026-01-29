from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass(frozen=True)
class SentimentResult:
    score: float  # [-1, 1]
    label: str  # "positive" | "negative" | "neutral"


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _label_for_score(score: float) -> str:
    if score >= 0.2:
        return "positive"
    if score <= -0.2:
        return "negative"
    return "neutral"


def _fallback_heuristic(text: str) -> SentimentResult:
    """
    Simple local heuristic so the app works even if SmartReview service isn't reachable.
    Replace/extend this by importing your SmartReview module if it's available locally.
    """
    t = (text or "").lower()
    pos = ["love", "great", "good", "amazing", "excellent", "fast", "easy", "helpful", "nice"]
    neg = ["hate", "bad", "terrible", "slow", "bug", "broken", "hard", "confusing", "awful"]
    score = 0.0
    score += sum(1.0 for w in pos if w in t)
    score -= sum(1.0 for w in neg if w in t)
    score = _clamp(score / 3.0, -1.0, 1.0)
    return SentimentResult(score=score, label=_label_for_score(score))


async def analyze_sentiment(text: str, *, timeout_s: float = 10.0) -> SentimentResult:
    """
    Tries SmartReview Sentiment Service over HTTP if SMARTREVIEW_URL is set.
    Expected SmartReview response (flexible):
      - { "score": 0.7 } or { "score": 0.7, "label": "positive" }
    Falls back to local heuristic otherwise.
    """
    base_url = os.getenv("SMARTREVIEW_URL", "").strip()
    if not base_url:
        return _fallback_heuristic(text)

    try:
        async with httpx.AsyncClient(timeout=timeout_s) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/sentiment/analyze",
                json={"text": text},
            )
            resp.raise_for_status()
            data: Any = resp.json()
            score = float(data.get("score", 0.0))
            score = _clamp(score, -1.0, 1.0)
            label: Optional[str] = data.get("label")
            if label not in ("positive", "negative", "neutral"):
                label = _label_for_score(score)
            return SentimentResult(score=score, label=label)
    except Exception:
        return _fallback_heuristic(text)

