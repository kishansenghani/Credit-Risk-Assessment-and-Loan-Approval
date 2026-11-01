import { useState, useEffect } from "react";
import Login from "./pages/Login";
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import "./App.css";

export default function App() {
  const [user, setUser] = useState(null);

  // Restore session from localStorage
  useEffect(() => {
    const stored = localStorage.getItem("loan_user");
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch {}
    }
  }, []);

  const handleLogin = (u) => setUser(u);

  const handleLogout = () => {
    localStorage.removeItem("loan_token");
    localStorage.removeItem("loan_user");
    setUser(null);
  };

  if (!user) return <Login onLogin={handleLogin} />;
  if (user.role === "admin")
    return <AdminDashboard user={user} onLogout={handleLogout} />;
  return <UserDashboard user={user} onLogout={handleLogout} />;
}
