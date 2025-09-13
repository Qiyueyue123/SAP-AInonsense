import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./AuthContext";
import PrivateRoute from "./PrivateRoute";
import Login from "./pages/Login";
import CreateAccount from "./pages/CreateAccount";
import Homepage from "./pages/Homepage";
import ResumeUpload from "./pages/ResumeUpload";
import Stats from "./pages/Stats";
import SidebarNav from "./components/sidenav";
import ResumeManager from './pages/ResumeManager';

// Optional component to conditionally redirect based on auth status
function RootRedirect() {
  const { user } = useAuth();
  return user ? <Navigate to="/homepage" replace /> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <div style={{
          display: "flex",
          width: "100vw",
          height: "100vh"
        }}>
          <SidebarNav />
          <main style={{
            flexGrow: 1,
            padding: "2rem 3rem",
            minHeight: "100vh",
            background: "transparent",
            overflowY: "auto"
          }}>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/create-account" element={<CreateAccount />} />

              {/* Root path redirects based on auth */}
              <Route path="/" element={<RootRedirect />} />

              {/* Private/protected routes */}
              <Route element={<PrivateRoute />}>
                <Route path="/homepage" element={<Homepage />} />
                <Route path="/resume-upload" element={<ResumeUpload />} />
                <Route path="/resume" element={<ResumeManager />} />
                <Route path="/stats" element={<Stats />} />
              </Route>
            </Routes>
          </main>
        </div>
      </AuthProvider>
    </Router>
  );
}
