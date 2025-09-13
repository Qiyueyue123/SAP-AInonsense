import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../AuthContext';

export default function SidebarNav() {
  const { logout } = useAuth();

  const linkStyle = { display: 'block', padding: '10px 15px', color: 'white', textDecoration: 'none', borderRadius: '5px', marginBottom: '5px' };
  const activeLinkStyle = { ...linkStyle, backgroundColor: '#0056b3' };

  return (
    <div style={{ width: '220px', height: '100vh', backgroundColor: '#007bff', padding: '20px', color: 'white', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{ borderBottom: '1px solid #fff', paddingBottom: '10px' }}>Aura AI</h3>
      <nav style={{ flexGrow: 1 }}>
        <NavLink to="/homepage" style={({ isActive }) => isActive ? activeLinkStyle : linkStyle}>Home</NavLink>
        <NavLink to="/resume-upload" style={({ isActive }) => isActive ? activeLinkStyle : linkStyle}>Upload Resume</NavLink>
        <NavLink to="/stats" style={({ isActive }) => isActive ? activeLinkStyle : linkStyle}>My Stats</NavLink> {/* <-- ADDED LINK */}
        <NavLink to="/career-coach" style={({ isActive }) => isActive ? activeLinkStyle : linkStyle}>Career Coach</NavLink>
      </nav>
      <button onClick={logout} style={{ width: '100%', padding: '10px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}>
        Logout
      </button>
    </div>
  );
}