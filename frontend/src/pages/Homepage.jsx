import { useAuth } from "../AuthContext";
import SidebarNav from "../components/sidenav";
import "./Homepage.css"; 

export default function Homepage() {
  const { logout, user } = useAuth();

  return (
    <div className="page-center">
      <SidebarNav />
      <div className="auth-card">
        <h2>Welcome {user?.email || "user"}!</h2>
        <p>You are now in the protected homepage.</p>
        <button onClick={logout}>Logout</button>
      </div>
    </div>
  );
}
