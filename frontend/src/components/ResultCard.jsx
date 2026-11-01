const RISK_CONFIG = {
  Low:    { color: "var(--accent-green)", bg: "rgba(16,185,129,0.12)", icon: "🟢" },
  Medium: { color: "#f59e0b",            bg: "rgba(245,158,11,0.12)", icon: "🟡" },
  High:   { color: "var(--accent-red)",  bg: "rgba(239,68,68,0.12)",  icon: "🔴" },
};

export default function ResultCard({ result }) {
  const approved   = result.prediction === "Approved";
  const confidence = (result.confidence * 100).toFixed(1);
  const riskCfg    = RISK_CONFIG[result.risk_band] || RISK_CONFIG["Medium"];

  // ── Top-3 SHAP reasons (structured from backend) ────────────────────────
  const topShap = result.top_shap || [];

  // ── Full SHAP bar chart (sorted by abs value, top 8) ─────────────────────
  const shapEntries = Object.entries(result.shap_values || {})
    .map(([k, v]) => ({ feature: k, value: v }))
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 8);
  const maxAbs = Math.max(...shapEntries.map((e) => Math.abs(e.value)), 0.001);

  return (
    <div className={`result-card ${approved ? "approved" : "rejected"}`}>

      {/* ── Verdict header ─────────────────────────────────────────────── */}
      <div className="verdict-header">
        <div className="verdict-icon">{approved ? "✅" : "❌"}</div>
        <div>
          <h2 className="verdict-label">{result.prediction}</h2>
          <p className="verdict-sub">
            AI Confidence: <strong>{confidence}%</strong>
          </p>
        </div>
      </div>

      {/* ── Confidence bar ─────────────────────────────────────────────── */}
      <div className="confidence-bar-wrap">
        <div className="confidence-bar-fill" style={{ width: `${confidence}%` }} />
      </div>

      {/* ── Risk Band badge ────────────────────────────────────────────── */}
      {result.risk_band && (
        <div
          className="risk-band-badge"
          style={{ background: riskCfg.bg, borderColor: riskCfg.color }}
        >
          <span>{riskCfg.icon}</span>
          <div>
            <span className="risk-band-label">Risk Band</span>
            <span className="risk-band-value" style={{ color: riskCfg.color }}>
              {result.risk_band} Risk
            </span>
          </div>
        </div>
      )}

      {/* ── Top 3 SHAP reasons (human-readable) ───────────────────────── */}
      {topShap.length > 0 && (
        <div className="top-reasons">
          <h3>🏆 Top 3 Decision Drivers</h3>
          <div className="reasons-list">
            {topShap.map((item, i) => (
              <div
                key={item.feature}
                className={`reason-item ${item.direction}`}
              >
                <span className="reason-rank">#{i + 1}</span>
                <span className="reason-feature">{item.feature.replace(/_/g, " ")}</span>
                <span className={`reason-dir ${item.direction}`}>
                  {item.direction === "positive" ? "▲ Favours approval" : "▼ Against approval"}
                </span>
                <span className="reason-val">
                  {item.value > 0 ? "+" : ""}{item.value.toFixed(4)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Full SHAP bar chart ────────────────────────────────────────── */}
      {shapEntries.length > 0 && (
        <div className="shap-section">
          <h3>🔍 Full Feature Impact (SHAP)</h3>
          <p className="shap-desc">Relative contribution of all features:</p>
          <div className="shap-bars">
            {shapEntries.map(({ feature, value }) => {
              const pct      = (Math.abs(value) / maxAbs) * 100;
              const positive = value >= 0;
              return (
                <div className="shap-row" key={feature}>
                  <span className="shap-feature">{feature}</span>
                  <div className="shap-bar-track">
                    <div
                      className={`shap-bar-fill ${positive ? "pos" : "neg"}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className={`shap-val ${positive ? "pos" : "neg"}`}>
                    {positive ? "+" : ""}{value.toFixed(4)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {result.note && (
        <p className="result-note">⚠️ {result.note}</p>
      )}
    </div>
  );
}
