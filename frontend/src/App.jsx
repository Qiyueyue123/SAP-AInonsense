import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import PrivateRoute from "./PrivateRoute";
import Login from "./pages/Login";
import CreateAccount from "./pages/CreateAccount";
import Homepage from "./pages/Homepage";
import Stats from "./pages/Stats";
import ResumeManager from "./pages/ResumeManager";
import SidebarNav from "./components/sidenav";
import ResumeUpload from './pages/ResumeUpload';  // adjust path


function RootRedirect() {
  const { user } = useAuth();
  return user ? <Navigate to="/homepage" replace /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <div style={{ display: "flex", width: "100vw", height: "100vh" }}>
          <SidebarNav />
          <main
            style={{
              flexGrow: 1,
              padding: "2rem 3rem",
              minHeight: "100vh",
              overflowY: "auto",
              background: "transparent",
            }}
          >
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/create-account" element={<CreateAccount />} />
              {/* Root route redirects based on auth */}
              <Route path="/" element={<RootRedirect />} />
              {/* Private/protected routes */}
              <Route element={<PrivateRoute />}>
                <Route path="/homepage" element={<Homepage />} />
                <Route path="/stats" element={<Stats />} />
                <Route path="/resume-manager" element={<ResumeManager />} />
                <Route path="/resume-upload" element={<ResumeUpload />} />
                {/* Add more private routes as needed */}
              </Route>
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </Router>
  );
}
