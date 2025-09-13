import React, { useState, useEffect } from 'react';

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  // Fetch chat history when component mounts
  useEffect(() => {
    fetch("/api/chat/history", { credentials: "include" })
      .then(res => res.json())
      .then(data => setMessages(data.chatHistory || []))
      .catch(() => setMessages([]));
  }, []);

  // Send user messages and receive bot replies
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: "user", text: input };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ message: input }),
      });
      const data = await response.json();
      setMessages(prev => [...prev, { sender: "bot", text: data.reply }]);
    } catch {
      setMessages(prev => [...prev, { sender: "bot", text: "Error: Unable to respond." }]);
    }

    setInput("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div
        style={{
          flexGrow: 1,
          minHeight: "450px",
          width: "420px",
          overflowY: "auto",
          padding: "1rem",
          border: "1px solid #ccc",
          background: "#fff",
          boxSizing: "border-box",
          borderRadius: "8px"
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              textAlign: m.sender === "user" ? "right" : "left",
              margin: "5px 0",
              color: m.sender === "user" ? "blue" : "green",
              whiteSpace: "pre-wrap"
            }}
          >
            {m.text}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", padding: "0.5rem", marginTop: "0.5rem" }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === "Enter") sendMessage(); }}
          placeholder="Type a message..."
          style={{ flexGrow: 1, marginRight: "0.5rem", padding: "0.5rem" }}
        />
        <button onClick={sendMessage} style={{
          padding: "0.5rem 1rem",
          backgroundColor: "#007bff",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}>
          Send
        </button>
      </div>
    </div>
  );
}
