import { useMemo, useState } from "react";
import type { AnalyzeBatchResponse, SentimentLabel } from "./api";
import { analyzeBatch } from "./api";
import { SentimentChart } from "./components/SentimentChart";

function splitLines(text: string): string[] {
  return text
    .split(/\r?\n/g)
    .map((l) => l.trim())
    .filter((l) => l.length > 0);
}

function pillClass(label: SentimentLabel) {
  if (label === "positive") return "pill pillPos";
  if (label === "negative") return "pill pillNeg";
  return "pill pillNeu";
}

export function App() {
  const [raw, setRaw] = useState(
    "Love the new search.\nThe app is slow after the last update.\nThis feature is okay, nothing special.\nGreat UX overall.\nConfusing settings page."
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeBatchResponse | null>(null);

  const lines = useMemo(() => splitLines(raw), [raw]);

  async function onAnalyze() {
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await analyzeBatch(lines);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <div>
          <div className="title">Feedback Insight Dashboard</div>
          <div className="subtitle">
            Paste a batch of feedback lines. Click Analyze. Get per-line sentiment + an overall mood snapshot.
          </div>
        </div>
      </header>

      <div className="grid">
        <div className="card">
          <div className="cardTitle">Input</div>
          <textarea
            className="textarea"
            rows={10}
            value={raw}
            onChange={(e) => setRaw(e.target.value)}
            placeholder="Paste one feedback comment per line…"
          />
          <div className="row">
            <div className="muted">
              Lines detected: <b>{lines.length}</b>
            </div>
            <button className="button" onClick={onAnalyze} disabled={loading || lines.length === 0}>
              {loading ? "Analyzing…" : "Analyze"}
            </button>
          </div>
          {error && <div className="error">{error}</div>}
        </div>

        {result && <SentimentChart stats={result.stats} />}

        {result && (
          <div className="card cardFull">
            <div className="cardTitle">Results</div>
            <div className="kpis">
              <div className="kpi">
                <div className="kpiLabel">Positive</div>
                <div className="kpiValue">{result.stats.positive_pct.toFixed(2)}%</div>
              </div>
              <div className="kpi">
                <div className="kpiLabel">Neutral</div>
                <div className="kpiValue">{result.stats.neutral_pct.toFixed(2)}%</div>
              </div>
              <div className="kpi">
                <div className="kpiLabel">Negative</div>
                <div className="kpiValue">{result.stats.negative_pct.toFixed(2)}%</div>
              </div>
              <div className="kpi">
                <div className="kpiLabel">Average score</div>
                <div className="kpiValue mono">{result.stats.avg_score.toFixed(4)}</div>
              </div>
            </div>

            <div className="tableWrap">
              <table className="table">
                <thead>
                  <tr>
                    <th style={{ width: "64%" }}>Comment</th>
                    <th style={{ width: "18%" }}>Sentiment</th>
                    <th style={{ width: "18%" }}>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {result.items.map((it, idx) => (
                    <tr key={idx}>
                      <td className="cellText">{it.text}</td>
                      <td>
                        <span className={pillClass(it.label)}>{it.label}</span>
                      </td>
                      <td className="mono">{it.score.toFixed(4)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      <footer className="footer">
        Backend: <span className="mono">/feedback/analyze-batch</span> • Proxy target configurable via{" "}
        <span className="mono">VITE_API_PROXY_TARGET</span>
      </footer>
    </div>
  );
}


