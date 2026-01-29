export type SentimentLabel = "positive" | "negative" | "neutral";

export interface FeedbackItemResult {
  text: string;
  score: number;
  label: SentimentLabel;
}

export interface AggregateStats {
  total: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
  avg_score: number;
}

export interface AnalyzeBatchResponse {
  items: FeedbackItemResult[];
  stats: AggregateStats;
}

export async function analyzeBatch(feedback: string[]): Promise<AnalyzeBatchResponse> {
  const resp = await fetch("/feedback/analyze-batch", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feedback })
  });
  if (!resp.ok) {
    const text = await resp.text().catch(() => "");
    throw new Error(`Analyze failed (${resp.status}): ${text || resp.statusText}`);
  }
  return (await resp.json()) as AnalyzeBatchResponse;
}


