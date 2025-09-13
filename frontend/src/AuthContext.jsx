import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";  // import here
import { setLogoutHandler } from "./axios";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();  // <- add this
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("authToken");
    if (stored) setUser(JSON.parse(stored));
    setReady(true);
  }, []);

  const login = (token, userData) => {
    localStorage.setItem("authToken", JSON.stringify({ token, ...userData }));
    setUser({ token, ...userData });
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setUser(null);
    navigate("/");  // Now this works
  };

  useEffect(() => {
    setLogoutHandler(logout);
  }, []);

  return (
    <AuthContext.Provider value={{ user, ready, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
