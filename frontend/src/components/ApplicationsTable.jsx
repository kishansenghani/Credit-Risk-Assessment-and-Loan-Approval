import { useState, useEffect } from "react";
import { getApplications, deleteApplication } from "../api/api";

const RISK_COLORS = {
  Low:    { color: "#6ee7b7", bg: "rgba(16,185,129,0.12)" },
  Medium: { color: "#fcd34d", bg: "rgba(245,158,11,0.12)" },
  High:   { color: "#f87171", bg: "rgba(239,68,68,0.12)"  },
};

export default function ApplicationsTable({ onSelect }) {
  const [apps, setApps]               = useState([]);
  const [loading, setLoading]         = useState(true);
  const [search, setSearch]           = useState("");
  const [statusFilter, setStatus]     = useState("");
  const [riskFilter, setRisk]         = useState("");
  const [page, setPage]               = useState(1);
  const [total, setTotal]             = useState(0);
  const perPage = 10;

  const fetchApps = async () => {
    setLoading(true);
    try {
      const { data } = await getApplications({
        page,
        per_page:  perPage,
        search:    search || undefined,
        status:    statusFilter || undefined,
        risk_band: riskFilter || undefined,
      });
      setApps(data.applications);
      setTotal(data.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchApps(); }, [page, statusFilter, riskFilter]);

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    fetchApps();
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this application?")) return;
    await deleteApplication(id);
    fetchApps();
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="table-container">
      {/* ── Filters ──────────────────────────────────────────────────────── */}
      <div className="table-filters">
        <form onSubmit={handleSearch} className="search-form">
          <input
            id="search-input"
            type="text"
            placeholder="Search by name…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn-secondary">Search</button>
        </form>

        <select
          id="status-filter"
          value={statusFilter}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
        >
          <option value="">All Status</option>
          <option value="Approved">Approved</option>
          <option value="Rejected">Rejected</option>
        </select>

        <select
          id="risk-filter"
          value={riskFilter}
          onChange={(e) => { setRisk(e.target.value); setPage(1); }}
        >
          <option value="">All Risk Bands</option>
          <option value="Low">🟢 Low</option>
          <option value="Medium">🟡 Medium</option>
          <option value="High">🔴 High</option>
        </select>
      </div>

      {/* ── Table ────────────────────────────────────────────────────────── */}
      {loading ? (
        <div className="table-loading"><div className="big-spinner" /></div>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Loan (₹K)</th>
                <th>Income (₹)</th>
                <th>Status</th>
                <th>Risk Band</th>
                <th>Confidence</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {apps.length === 0 ? (
                <tr>
                  <td colSpan={9} className="empty-row">No applications found.</td>
                </tr>
              ) : apps.map((a) => {
                const rc = RISK_COLORS[a.risk_band] || RISK_COLORS["Medium"];
                return (
                  <tr key={a.id} className="table-row">
                    <td>#{a.id}</td>
                    <td>{a.applicant_name}</td>
                    <td>{a.loan_amount}</td>
                    <td>{a.applicant_income?.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${a.prediction === "Approved" ? "badge-green" : "badge-red"}`}>
                        {a.prediction}
                      </span>
                    </td>
                    <td>
                      {a.risk_band ? (
                        <span
                          className="badge"
                          style={{ background: rc.bg, color: rc.color }}
                        >
                          {a.risk_band}
                        </span>
                      ) : "—"}
                    </td>
                    <td>
                      {a.confidence ? `${(a.confidence * 100).toFixed(1)}%` : "—"}
                    </td>
                    <td>{new Date(a.submitted_at).toLocaleDateString()}</td>
                    <td className="action-cell">
                      <button
                        id={`view-app-${a.id}`}
                        className="btn-icon"
                        onClick={() => onSelect && onSelect(a)}
                        title="View details"
                      >👁️</button>
                      <button
                        id={`del-app-${a.id}`}
                        className="btn-icon danger"
                        onClick={() => handleDelete(a.id)}
                        title="Delete"
                      >🗑️</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Pagination ────────────────────────────────────────────────────── */}
      <div className="pagination">
        <button
          id="prev-page"
          className="btn-secondary"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1}
        >← Prev</button>
        <span>Page {page} of {totalPages || 1}  &nbsp;·&nbsp;  {total} total</span>
        <button
          id="next-page"
          className="btn-secondary"
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages}
        >Next →</button>
      </div>
    </div>
  );
}
