import React, { useState, useEffect, useRef } from "react";
import { useAuth } from "../AuthContext"; // adjust path if needed
import "./Chatbot.css";

export default function Chatbot() {
  const { user } = useAuth();              // expects { token, ...userData }
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // auto-scroll to the latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  useEffect(scrollToBottom, [messages]);

  // Fetch chat history when user is available
  useEffect(() => {
    if (!user?.token) return;

    const fetchHistory = async () => {
      try {
        const res = await fetch(`${import.meta.env.VITE_BACKEND_API}/api/chat/history`, {
          headers: {
            Authorization: `Bearer ${user.token}`,
          },
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        // Expecting backend history as [{role:'user'|'assistant', content:'...'}]
        const formatted = (data?.chatHistory || []).map((m) => ({
          sender: m.role === "user" ? "user" : "bot",
          text: m.content,
        }));
        setMessages(formatted);
      } catch (err) {
        console.error("Failed to fetch chat history:", err);
        setMessages([]); // safe fallback
      }
    };

    fetchHistory();
  }, [user?.token]);

  // Send user messages and receive bot replies
  const sendMessage = async () => {
    if (!input.trim() || !user?.token || isLoading) return;

    const text = input;
    setInput(""); // clear immediately for snappy UX
    setIsLoading(true);

    // add user's message right away
    setMessages((prev) => [...prev, { sender: "user", text }]);

    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_API}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user.token}`,
        },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: data?.reply ?? "…" },
      ]);
    } catch (e) {
      console.error(e);
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error: Unable to respond." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-messages">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`chatbot-message ${m.sender === "user" ? "user" : "bot"}`}
          >
            {m.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chatbot-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }}
          placeholder={user ? "Type a message..." : "Log in to chat"}
          className="chatbot-input"
          disabled={!user || isLoading}
        />
        <button
          onClick={sendMessage}
          className="chatbot-send-button"
          disabled={!user || isLoading}
        >
          {isLoading ? "…" : "Send"}
        </button>
      </div>
    </div>
  );
}
