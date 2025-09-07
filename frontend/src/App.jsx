import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import PrivateRoute from "./PrivateRoute";
import Login from "./pages/Login";
import CreateAccount from "./pages/CreateAccount";
import Homepage from "./pages/Homepage";

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/penis" element={<h1>Penis</h1>} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />

          <Route element={<PrivateRoute />}>
            <Route path="/homepage" element={<Homepage />} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}
