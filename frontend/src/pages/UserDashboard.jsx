import { useState } from "react";
import LoanForm from "../components/LoanForm";
import ResultCard from "../components/ResultCard";
import { predict } from "../api/api";
import "./UserDashboard.css";

export default function UserDashboard({ user, onLogout }) {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handlePredict = async (formData) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const { data } = await predict(formData);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.error || "Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <span className="logo-icon">⬡</span>
          <span>LoanIQ</span>
        </div>
        <nav className="sidebar-nav">
          <a className="nav-item active" href="#">🏠 Dashboard</a>
        </nav>
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="avatar">{user.username[0].toUpperCase()}</div>
            <div>
              <p className="username">{user.username}</p>
              <p className="role">{user.role}</p>
            </div>
          </div>
          <button id="logout-btn" className="logout-btn" onClick={onLogout}>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <header className="content-header">
          <div>
            <h1>Loan Application</h1>
            <p>Fill in the form below to get an instant AI credit decision.</p>
          </div>
        </header>

        <div className="apply-grid">
          <section className="form-section">
            <ApplyLoan onSubmit={handlePredict} loading={loading} />
          </section>

          <section className="result-section">
            {error && <p className="form-error">{error}</p>}
            {result && <ResultCard result={result} />}
            {!result && !error && !loading && (
              <div className="empty-state">
                <span className="empty-icon">🤖</span>
                <p>Your AI prediction will appear here after you submit.</p>
              </div>
            )}
            {loading && (
              <div className="empty-state">
                <div className="big-spinner" />
                <p>Analyzing your application…</p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

// Inline ApplyLoan panel (also available as its own page)
function ApplyLoan({ onSubmit, loading }) {
  return <LoanForm onSubmit={onSubmit} loading={loading} />;
}
