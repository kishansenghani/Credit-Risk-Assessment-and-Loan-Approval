import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer,
  LineChart, Line,
} from "recharts";
import { getAnalytics } from "../api/api";

// Consistent palette
const STATUS_COLORS  = { Approved: "#6ee7b7", Rejected: "#f87171" };
const RISK_COLORS    = { Low: "#6ee7b7", Medium: "#fcd34d", High: "#f87171" };
const CHART_TOOLTIP  = { background: "#1e293b", border: "none", borderRadius: 8 };
const AXIS_STYLE     = { stroke: "#94a3b8", fontSize: 12 };
const GRID_STYLE     = { strokeDasharray: "3 3", stroke: "#334155" };

export default function AnalyticsCharts() {
  const [data, setData]     = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]   = useState("");

  useEffect(() => {
    getAnalytics()
      .then(({ data: d }) => setData(d))
      .catch(() => setError("Failed to load analytics. Make sure the backend is running."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="big-spinner" style={{ margin: "4rem auto" }} />;
  if (error)   return <p className="form-error">{error}</p>;
  if (!data)   return <p style={{ color: "var(--muted)" }}>No data yet.</p>;

  const { kpis, approval_by_area, approval_by_education,
          risk_band_distribution, monthly_trend } = data;

  // ── Pie data for risk band ──────────────────────────────────────────────
  const riskPieData = risk_band_distribution.map((r) => ({
    name:  r.risk_band,
    value: r.count,
    fill:  RISK_COLORS[r.risk_band] || "#94a3b8",
  }));

  return (
    <div className="charts-grid">

      {/* ── KPI Cards ─────────────────────────────────────────────────────── */}
      <div className="kpi-row">
        <div className="kpi-card">
          <span className="kpi-label">Total Applications</span>
          <span className="kpi-value">{kpis.total}</span>
        </div>
        <div className="kpi-card approved">
          <span className="kpi-label">Approved</span>
          <span className="kpi-value">{kpis.approved}</span>
        </div>
        <div className="kpi-card rejected">
          <span className="kpi-label">Rejected</span>
          <span className="kpi-value">{kpis.rejected}</span>
        </div>
        <div className="kpi-card">
          <span className="kpi-label">Approval Rate</span>
          <span className="kpi-value">{kpis.approval_rate}%</span>
        </div>
      </div>

      {/* ── Charts row 1: Property Area + Education ────────────────────────── */}
      <div className="charts-row-2">

        {/* Approval by Property Area — grouped bar */}
        <div className="chart-card">
          <h3>📍 Approval by Property Area</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={approval_by_area} barGap={4} barCategoryGap="30%">
              <CartesianGrid {...GRID_STYLE} />
              <XAxis dataKey="area" {...AXIS_STYLE} />
              <YAxis {...AXIS_STYLE} />
              <Tooltip contentStyle={CHART_TOOLTIP} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Approved" fill={STATUS_COLORS.Approved} radius={[4, 4, 0, 0]} />
              <Bar dataKey="Rejected" fill={STATUS_COLORS.Rejected} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Approval by Education — grouped bar */}
        <div className="chart-card">
          <h3>🎓 Approval by Education</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={approval_by_education} barGap={4} barCategoryGap="30%">
              <CartesianGrid {...GRID_STYLE} />
              <XAxis dataKey="education" {...AXIS_STYLE} />
              <YAxis {...AXIS_STYLE} />
              <Tooltip contentStyle={CHART_TOOLTIP} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="Approved" fill={STATUS_COLORS.Approved} radius={[4, 4, 0, 0]} />
              <Bar dataKey="Rejected" fill={STATUS_COLORS.Rejected} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Charts row 2: Risk Band Pie + Monthly Trend ─────────────────────── */}
      <div className="charts-row-2">

        {/* Risk Band Distribution — donut */}
        <div className="chart-card">
          <h3>⚠️ Risk Band Distribution</h3>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={riskPieData}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={110}
                paddingAngle={4}
                dataKey="value"
              >
                {riskPieData.map((entry, i) => (
                  <Cell key={i} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip contentStyle={CHART_TOOLTIP} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>

          {/* Risk legend with counts */}
          <div className="risk-legend">
            {riskPieData.map((r) => (
              <div key={r.name} className="risk-legend-item">
                <span className="risk-dot" style={{ background: r.fill }} />
                <span>{r.name}</span>
                <strong>{r.value}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Monthly Application Trend — line */}
        <div className="chart-card">
          <h3>📈 Monthly Application Trend</h3>
          {monthly_trend.length === 0 ? (
            <div className="empty-state" style={{ padding: "3rem 0" }}>
              <p>No trend data yet — submit some applications first.</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={monthly_trend}>
                <CartesianGrid {...GRID_STYLE} />
                <XAxis dataKey="month" {...AXIS_STYLE} />
                <YAxis {...AXIS_STYLE} />
                <Tooltip contentStyle={CHART_TOOLTIP} />
                <Line
                  type="monotone"
                  dataKey="applications"
                  stroke="#6366f1"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: "#6366f1" }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* ── Avg loan by verdict ────────────────────────────────────────────── */}
      <div className="chart-card">
        <h3>💰 Avg Loan Amount by Decision (₹K)</h3>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart
            data={[
              { name: "Approved", avg_loan: kpis.avg_loan_approved },
              { name: "Rejected", avg_loan: kpis.avg_loan_rejected },
            ]}
            barSize={60}
          >
            <CartesianGrid {...GRID_STYLE} />
            <XAxis dataKey="name" {...AXIS_STYLE} />
            <YAxis {...AXIS_STYLE} />
            <Tooltip contentStyle={CHART_TOOLTIP} />
            <Bar dataKey="avg_loan" radius={[6, 6, 0, 0]}>
              <Cell fill={STATUS_COLORS.Approved} />
              <Cell fill={STATUS_COLORS.Rejected} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

    </div>
  );
}
