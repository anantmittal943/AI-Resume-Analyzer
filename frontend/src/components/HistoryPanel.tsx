import type { Analysis } from "../types/models";

type Props = {
  analyses: Analysis[];
};

export default function HistoryPanel({ analyses }: Props) {
  if (analyses.length === 0) {
    return (
      <section className="panel history-panel">
        <h3>Analysis History</h3>
        <p className="muted">No analyses yet. Run your first evaluation.</p>
      </section>
    );
  }

  return (
    <section className="panel history-panel">
      <h3>Analysis History</h3>
      <ul className="history-list">
        {analyses.map((analysis) => (
          <li key={analysis.id}>
            <div>
              <strong>Score {analysis.suitability_score}</strong>
              <p className="muted">{new Date(analysis.created_at).toLocaleString()}</p>
            </div>
            <p>{analysis.summary}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
