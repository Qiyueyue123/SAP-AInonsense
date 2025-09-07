// src/pages/Login.jsx
import "./Login.css";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { useAuth } from "../AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const email = e.target.email.value.trim();
    const password = e.target.password.value;

    try {
      // Debug: see the attempt in the console
      console.log("[Login] submitting", email);
      const cred = await signInWithEmailAndPassword(auth, email, password);

      // Get Firebase ID token (JWT)
      const idToken = await cred.user.getIdToken();
      // Update your AuthContext (stores token in localStorage)
      login(idToken, { email: cred.user.email, uid: cred.user.uid });
      navigate("/homepage", { replace: true });
    } catch (err) {
      console.error("[Login] error:", err);
      // Friendly messages for common Firebase Auth errors
      const code = err?.code || "";
      if (
        code === "auth/invalid-credential" ||
        code === "auth/wrong-password"
      ) {
        setError("Invalid email or password.");
      } else if (code === "auth/user-not-found") {
        setError("No account found for that email.");
      } else if (code === "auth/too-many-requests") {
        setError("Too many attempts. Try again later.");
      } else if (code === "auth/network-request-failed") {
        setError("Network error. Check your connection.");
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

return (
  <div className="page-center">
    <div className="login-container">
      <h2>Login</h2>
      <form className="login-form" onSubmit={handleSubmit}>
        <label>Email</label>
        <input name="email" type="email" required />
        <label>Password</label>
        <input name="password" type="password" required />
        {error && (
            <p className="error" role="alert" aria-live="assertive">
              {error}
            </p>
          )}
        <button type="submit">Login</button>
      </form>
      <p className="hint">
        Don't have an account? <Link to="/create-account">Register</Link>
      </p>
    </div>
  </div>
);
}