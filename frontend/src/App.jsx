import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import PrivateRoute from "./PrivateRoute";
import Login from "./pages/Login";
import CreateAccount from "./pages/CreateAccount";
import Homepage from "./pages/Homepage";
import ResumeUpload from "./pages/ResumeUpload";
import SidebarNav from "./components/sidenav";
import Stats from "./pages/Stats";
import ResumeManager from './pages/ResumeManager';

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
              <Route path="/login" element={<Login />} />
              <Route path="/create-account" element={<CreateAccount />} />
              <Route path="/" element={<Navigate to="/homepage" replace />} />
              {/* Private routes */}
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



