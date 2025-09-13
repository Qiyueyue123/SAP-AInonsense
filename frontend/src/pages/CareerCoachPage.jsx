import React from 'react';
import Chatbot from '../components/Chatbot';
import SidebarNav from '../components/SidebarNav';

export default function CareerCoachPage() {
  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <SidebarNav />
      <div className="page-center" style={{ flexGrow: 1, padding: '2rem' }}>
        <div className="auth-card">
          <h2>Aura, Your Career Coach</h2>
          <p>Ask me for career advice, course recommendations, or to find a mentor!</p>
          <Chatbot />
        </div>
      </div>
    </div>
  );
}