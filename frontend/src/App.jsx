import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import PrivateRoute from "./PrivateRoute";
import Login from "./pages/Login";
import CreateAccount from "./pages/CreateAccount";
import Homepage from "./pages/Homepage";
import ResumeUpload from "./pages/ResumeUpload";
import Stats from "./pages/Stats"


export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/penis" element={<h1>Penis</h1>} />
          <Route path="/create-account" element={<CreateAccount />} />

          <Route element={<PrivateRoute />}>
            <Route path="/homepage" element={<Homepage />} />
            <Route path="/resume-upload" element={<ResumeUpload />} />
            <Route path="/stats" element={<Stats />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}
