import { useState } from "react";
import { NavLink } from "react-router-dom";
import "./sidenav.css";

const SidebarNav = ({ children, title = "Career Coach" }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Toggle button (moves with sidebar) */}
      <button
        className="sidebar-toggle"
        onClick={toggleSidebar}
        style={{
          left: isOpen ? "260px" : "20px", // push right when sidebar open
          background: isOpen
            ? "rgba(41, 128, 185, 0.3)"
            : "rgba(41, 128, 185, 0.6)",
        }}
      >
        {isOpen ? "✖" : "☰"}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${isOpen ? "open" : ""}`}>
        <h2 style={{ color: "#ecf0f1", marginBottom: "20px" }}>{title}</h2>
        <nav className="sidebar-links">
          <NavLink
            to="/homepage"
            className={({ isActive }) => (isActive ? "active-link" : "")}
          >
            Home
          </NavLink>
          <NavLink
            to="/resume-upload"
            className={({ isActive }) => (isActive ? "active-link" : "")}
          >
            Resume Upload
          </NavLink>
          <NavLink
            to="/stats"
            className={({ isActive }) => (isActive ? "active-link" : "")}
          >
            Stats
          </NavLink>
          <NavLink
            to="/career-path"
            className={({ isActive }) => (isActive ? "active-link" : "")}
          >
            Career Path
          </NavLink>
        </nav>
      </aside>

      {/* Main content shifts when sidebar is open */}
      <main className={`main-content ${isOpen ? "shift" : ""}`}>
        {children}
      </main>
    </>
  );
};

export default SidebarNav;
