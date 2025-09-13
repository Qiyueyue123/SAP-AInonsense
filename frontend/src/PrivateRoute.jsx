import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./AuthContext";

export default function PrivateRoute() {
  const { user, ready } = useAuth();
  if (!ready) return null;
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}
