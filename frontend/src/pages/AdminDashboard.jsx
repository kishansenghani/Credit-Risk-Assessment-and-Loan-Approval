import { useState } from "react";
import ApplicationsTable from "../components/ApplicationsTable";
import AnalyticsCharts from "../components/AnalyticsCharts";
import "./AdminDashboard.css";

const TABS = ["📊 Analytics", "📋 Applications"];

export default function AdminDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState(0);
  const [selected, setSelected] = useState(null);

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">⬡</span>
          <span>LoanIQ</span>
        </div>
        <div className="sidebar-badge">Admin Panel</div>
        <nav className="sidebar-nav">
          {TABS.map((tab, i) => (
            <button
              key={i}
              id={`tab-${i}`}
              className={`nav-item ${activeTab === i ? "active" : ""}`}
              onClick={() => setActiveTab(i)}
            >
              {tab}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar admin">{user.username[0].toUpperCase()}</div>
            <div>
              <p className="username">{user.username}</p>
              <p className="role">{user.role}</p>
            </div>
          </div>
          <button id="admin-logout-btn" className="logout-btn" onClick={onLogout}>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="main-content">
        <header className="content-header">
          <div>
            <h1>{TABS[activeTab].replace(/^.+ /, "")}</h1>
            <p>
              {activeTab === 0
                ? "Overview of all loan applications and model performance."
                : "Browse, search, and manage all submitted loan applications."}
            </p>
          </div>
        </header>

        {activeTab === 0 && <AnalyticsCharts />}
        {activeTab === 1 && (
          <ApplicationsTable onSelect={(a) => setSelected(a)} />
        )}

        {/* Detail modal */}
        {selected && (
          <div className="modal-overlay" onClick={() => setSelected(null)}>
            <div className="modal-card" onClick={(e) => e.stopPropagation()}>
              <h3>Application #{selected.id}</h3>
              <div className="detail-grid">
                {Object.entries(selected).map(([k, v]) => {
                  if (k === "top_shap") {
                    const shapList = Array.isArray(v)
                      ? v
                      : typeof v === "string"
                      ? (() => {
                          try {
                            return JSON.parse(v);
                          } catch {
                            return [];
                          }
                        })()
                      : [];

                    return (
                      <div key={k} className="detail-row detail-row-shap">
                        <span className="detail-key">Top SHAP Drivers</span>
                        <div className="detail-val shap-lines-list">
                          {shapList.length === 0 ? (
                            <span>—</span>
                          ) : (
                            shapList.map((item, idx) => {
                              const isPositive =
                                item.direction === "positive" || item.value >= 0;
                              const action = isPositive
                                ? "pushed towards approval"
                                : "pushed against approval";
                              const valNum =
                                typeof item.value === "number"
                                  ? item.value
                                  : parseFloat(item.value);
                              const formattedVal = !isNaN(valNum)
                                ? `${valNum > 0 ? "+" : ""}${valNum.toFixed(2)}`
                                : item.value;

                              return (
                                <div
                                  key={item.feature || idx}
                                  className={`shap-readable-line ${isPositive ? "positive" : "negative"}`}
                                >
                                  <strong>{item.feature}</strong>: {action} ({formattedVal})
                                </div>
                              );
                            })
                          )}
                        </div>
                      </div>
                    );
                  }

                  return (
                    <div key={k} className="detail-row">
                      <span className="detail-key">{k.replace(/_/g, " ")}</span>
                      <span className="detail-val">{String(v ?? "—")}</span>
                    </div>
                  );
                })}
              </div>
              <button
                id="close-modal"
                className="btn-secondary"
                onClick={() => setSelected(null)}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
