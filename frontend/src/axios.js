import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_API,
  headers: { "Content-Type": "application/json" }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("authToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let logoutHandler = null;

export const setLogoutHandler = (fn) => {
  logoutHandler = fn;
};

// Response interceptor
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const status = err.response?.status;

    if (status === 401 || status === 403) {
      if (logoutHandler) {
        logoutHandler(); // call AuthContext’s logout()
      }
    }

    return Promise.reject(err);
  }
);

export default api;