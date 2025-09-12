
import { NavLink } from 'react-router-dom';
import './sideNav.css';

const SidebarNav = () => {
  return (
    <aside className="sidebar">
      <nav className="sidebar-links">
        <NavLink to="/homepage" className={({ isActive }) => (isActive ? "active-link" : "")}>Home</NavLink>
        <NavLink to="/resume-upload" className={({ isActive }) => (isActive ? "active-link" : "")}>Resume Upload</NavLink>
        <NavLink to="/stats" className={({ isActive }) => (isActive ? "active-link" : "")}>Stats</NavLink>
      </nav>
    </aside>
  );
};

export default SidebarNav;
