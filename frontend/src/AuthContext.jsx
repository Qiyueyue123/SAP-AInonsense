import { createContext, useContext, useEffect, useState } from "react";
import { setLogoutHandler } from "./axios";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) setUser({ token });
    setReady(true);
  }, []);

  const login = (token, userData) => {
    localStorage.setItem("authToken", token);
    setUser({ token, ...userData });
  };

  const logout = () => {
    localStorage.removeItem("authToken");
    setUser(null);
    window.location = "/"; // <-- or similar, since navigate() wasn't used
  };

  useEffect(() => {
    setLogoutHandler(logout);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout, ready }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
