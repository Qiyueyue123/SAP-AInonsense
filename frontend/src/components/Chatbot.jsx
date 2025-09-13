import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../AuthContext';

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { currentUser } = useAuth();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentUser) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const token = await currentUser.getIdToken();
      const history = messages.map(({ role, content }) => ({ role, content }));

      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_API}/api/chat`,
        { message: userMessage.content, history: history },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      const aiMessage = response.data;
      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { role: 'assistant', content: 'Sorry, I ran into an error. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ height: '70vh', display: 'flex', flexDirection: 'column', border: '1px solid #ccc', borderRadius: '8px', marginTop: '1rem' }}>
      <div style={{ flexGrow: 1, overflowY: 'auto', padding: '1rem' }}>
        {messages.map((msg, index) => (
          <div key={index} style={{ marginBottom: '1rem', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
            <div style={{
              display: 'inline-block',
              padding: '0.5rem 1rem',
              borderRadius: '15px',
              backgroundColor: msg.role === 'user' ? '#007bff' : '#f1f1f1',
              color: msg.role === 'user' ? 'white' : 'black',
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} style={{ display: 'flex', padding: '1rem', borderTop: '1px solid #ccc' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask for a recommendation..."
          disabled={isLoading}
          style={{ flexGrow: 1, padding: '0.5rem', borderRadius: '5px', border: '1px solid #ccc' }}
        />
        <button type="submit" disabled={isLoading} style={{ marginLeft: '0.5rem', padding: '0.5rem 1rem', cursor: 'pointer' }}>
          {isLoading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
}