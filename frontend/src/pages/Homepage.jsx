import { useAuth } from "../AuthContext";
import { Link } from 'react-router-dom';
import './Homepage.css';

export default function Homepage() {
  const { logout, user } = useAuth();

  return (
    <div className="page-center">
      <div className="auth-card">
        <h2>Welcome {user?.email || "user"}!</h2>
        <p>You are now in the protected homepage.</p>

        <Link to="/resume" className="resume-link">
          Go to Resume Manager
        </Link>

        <button onClick={logout} className="logout-button">
          Logout
        </button>
      </div>
    </div>
  );
}
