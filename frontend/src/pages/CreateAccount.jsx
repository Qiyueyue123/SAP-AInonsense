import "./CreateAccount.css";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { useAuth } from "../AuthContext";
import api from "../axios.js"
export default function CreateAccount() {
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
    const confirm = e.target.confirm.value;

    if (password !== confirm) {
      setError("Passwords do not match.");
      setLoading(false);
      return;
    }

    try {
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      const idToken = await cred.user.getIdToken();
      // store token + basic user in your AuthContext (same as Login)
      login(idToken, { email: cred.user.email, uid: cred.user.uid });
      const stuff = {
        email: cred.user.email,
        uid: cred.user.uid
      }
      const response = await api.post("/create-account", stuff)

      if (response.status === 200) {
        console.log("Account created:", response.data);
      } else if (response.status === 400) {
        console.error("Error:", response.data.message);
      } else {
        console.error("Unexpected error:", response.status, response.data);
      }

      navigate("/homepage", { replace: true });
    } catch (err) {
      console.error("[CreateAccount] error:", err);
      const code = err?.code || "";
      if (code === "auth/email-already-in-use") setError("Email already in use.");
      else if (code === "auth/weak-password") setError("Password is too weak.");
      else if (code === "auth/invalid-email") setError("Invalid email.");
      else if (code === "auth/operation-not-allowed") setError("Email/password sign-in is disabled in Firebase.");
      else setError("Sign up failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">
      <div className="auth-card">
        <h2>Create Account</h2>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label>Email</label>
          <input name="email" type="email" autoComplete="username" required />

          <label>Password</label>
          <input name="password" type="password" autoComplete="new-password" required />

          <label>Confirm Password</label>
          <input name="confirm" type="password" autoComplete="new-password" required />

          {error && <p className="error">{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>

        <p className="hint">
          Already have an account? <Link to="/">Log in</Link>
        </p>
      </div>
    </div>
  );
}
