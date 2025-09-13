import { useAuth } from "../AuthContext";
import { Link } from 'react-router-dom';

export default function Homepage() {
  const { logout, user } = useAuth();

  return (
    <div className="page-center">
      <div className="auth-card">
        <h2>Welcome {user?.email || "user"}!</h2>
        <p>You are now in the protected homepage.</p>

        <Link to="/resume" style={{ display: 'block', margin: '1rem 0' }}>
          Go to Resume Manager
        </Link>

        <button onClick={logout} style={{ marginTop: "1rem" }}>
          Logout
        </button>
      </div>
    </div>
  );
}
