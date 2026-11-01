import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Auth token injection ────────────────────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("loan_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Response error handling ─────────────────────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("loan_token");
      localStorage.removeItem("loan_user");
      window.location.href = "/";
    }
    return Promise.reject(err);
  }
);

// ── Auth ────────────────────────────────────────────────────────────────────
export const login = (username, password) =>
  api.post("/login", { username, password });

export const register = (username, password, role = "user") =>
  api.post("/register", { username, password, role });

// ── Prediction ───────────────────────────────────────────────────────────────
export const predict = (formData) => api.post("/predict", formData);

// ── Applications (admin) ─────────────────────────────────────────────────────
export const getApplications = (params) => api.get("/applications", { params });
export const getApplication  = (id)     => api.get(`/applications/${id}`);
export const deleteApplication = (id)   => api.delete(`/applications/${id}`);

// ── Analytics ────────────────────────────────────────────────────────────────
export const getAnalytics = ()  => api.get("/analytics");
export const getStats     = ()  => api.get("/applications/stats"); // kept for compat

export default api;
