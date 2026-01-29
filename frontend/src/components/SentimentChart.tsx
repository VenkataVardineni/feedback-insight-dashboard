import type { AggregateStats } from "../api";

function pctLabel(v: number) {
  return `${v.toFixed(2)}%`;
}

export function SentimentChart({ stats }: { stats: AggregateStats }) {
  const p = stats.positive_pct;
  const n = stats.negative_pct;
  const u = stats.neutral_pct;

  // Simple stacked bar (no external chart deps)
  return (
    <div className="card">
      <div className="cardTitle">Mood distribution</div>
      <div className="stackedBar" role="img" aria-label="Sentiment distribution">
        <div className="seg segPos" style={{ width: `${p}%` }} title={`Positive ${pctLabel(p)}`} />
        <div className="seg segNeu" style={{ width: `${u}%` }} title={`Neutral ${pctLabel(u)}`} />
        <div className="seg segNeg" style={{ width: `${n}%` }} title={`Negative ${pctLabel(n)}`} />
      </div>
      <div className="legend">
        <div className="legendItem">
          <span className="dot dotPos" /> Positive: <b>{pctLabel(p)}</b>
        </div>
        <div className="legendItem">
          <span className="dot dotNeu" /> Neutral: <b>{pctLabel(u)}</b>
        </div>
        <div className="legendItem">
          <span className="dot dotNeg" /> Negative: <b>{pctLabel(n)}</b>
        </div>
      </div>
    </div>
  );
}


