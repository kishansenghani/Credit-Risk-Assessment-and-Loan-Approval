import { useState } from "react";
import { login } from "../api/api";
import "./Login.css";

export default function Login({ onLogin }) {
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) =>
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await login(form.username, form.password);
      localStorage.setItem("loan_token", data.token);
      localStorage.setItem("loan_user", JSON.stringify(data.user));
      onLogin(data.user);
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Left Panel */}
      <div className="login-hero">
        <div className="hero-content">
          <div className="hero-logo">
            <span className="logo-icon">⬡</span>
            <span className="logo-text">LoanIQ</span>
          </div>
          <h1>AI-Powered Loan Risk Analysis</h1>
          <p>Get instant credit decisions backed by machine learning and explainable AI.</p>
          <div className="hero-stats">
            <div className="stat"><strong>98.2%</strong><span>Accuracy</span></div>
            <div className="stat"><strong>&lt;2s</strong><span>Decision Time</span></div>
            <div className="stat"><strong>SHAP</strong><span>Explainability</span></div>
          </div>
        </div>
      </div>

      {/* Right Panel – Form */}
      <div className="login-form-panel">
        <div className="login-card">
          <h2>Welcome back</h2>
          <p className="login-sub">Sign in to your account</p>

          <form onSubmit={handleSubmit} className="login-form">
            <div className="field-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                value={form.username}
                onChange={handleChange}
                placeholder="Enter username"
                autoComplete="username"
                required
              />
            </div>

            <div className="field-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Enter password"
                autoComplete="current-password"
                required
              />
            </div>

            {error && <p className="form-error">{error}</p>}

            <button
              type="submit"
              id="login-submit"
              className="btn-primary"
              disabled={loading}
            >
              {loading ? <span className="spinner" /> : "Sign In"}
            </button>
          </form>

          <p className="demo-hint">
            Demo: <strong>admin / admin123</strong> &nbsp;|&nbsp; <strong>user / user123</strong>
          </p>
        </div>
      </div>
    </div>
  );
}
