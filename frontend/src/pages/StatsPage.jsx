import React, { useState, useEffect } from 'react';
import { useAuth } from '../AuthContext';
import { firestore } from '../firebase';
import { doc, getDoc } from 'firebase/firestore';
import SidebarNav from '../components/SidebarNav';

export default function StatsPage() {
  const { currentUser } = useAuth();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchUserData = async () => {
      if (!currentUser) {
        setLoading(false);
        return;
      }
      try {
        const userDocRef = doc(firestore, 'users', currentUser.uid);
        const userDoc = await getDoc(userDocRef);
        if (userDoc.exists()) {
          setUserData(userDoc.data());
        } else {
          setError('No data found. Please upload a resume first.');
        }
      } catch (err) {
        setError('Failed to fetch user data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, [currentUser]);

  if (loading) {
    return (
      <div style={{ display: 'flex', height: '100vh' }}>
        <SidebarNav />
        <div className="page-center">Loading your stats...</div>
      </div>
    );
  }
  
  if (error) {
     return (
      <div style={{ display: 'flex', height: '100vh' }}>
        <SidebarNav />
        <div className="page-center">Error: {error}</div>
      </div>
    );
  }

  const { skillScores, qualitativeFeedback } = userData || {};

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <SidebarNav />
      <div className="page-center" style={{ flexGrow: 1, padding: '2rem', overflowY: 'auto' }}>
        <div className="auth-card">
          <h2>Your Skill Analysis</h2>
          
          {qualitativeFeedback && (
            <div style={{ marginBottom: '2rem', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
              <h4>AI Feedback</h4>
              <p><strong>Strengths:</strong> {qualitativeFeedback.strengths}</p>
              <p><strong>Weaknesses:</strong> {qualitativeFeedback.weaknesses}</p>
            </div>
          )}

          <h4>Skill Scores (out of 20)</h4>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
            {skillScores && Object.entries(skillScores).map(([skill, score]) => (
              <div key={skill} style={{ marginBottom: '0.5rem' }}>
                <strong>{skill}</strong>
                <div style={{ backgroundColor: '#e9ecef', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${(score / 20) * 100}%`,
                    backgroundColor: '#007bff',
                    padding: '5px 8px',
                    color: 'white',
                    textAlign: 'right',
                    minWidth: '40px',
                    boxSizing: 'border-box'
                  }}>
                    {score}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}