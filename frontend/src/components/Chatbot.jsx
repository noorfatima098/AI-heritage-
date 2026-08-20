import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./Chatbot.css";

export default function Chatbot({ currentLandmarkId }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "bot", text: "Assalam o Alaikum! 🕌 I am your AI Heritage Guide for Lahore Fort. Ask me anything — or say 'Where am I?' to discover your location!" }
  ])
  const API = process.env.REACT_APP_API_URL || "http://localhost:8000";;
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [location, setLocation] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    navigator.geolocation?.getCurrentPosition(
      pos => setLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {}
    );
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim()) return;
    const userMsg = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setLoading(true);

    try {
      const form = new FormData();
      form.append("message", userMsg);
      if (location) {
        form.append("lat", location.lat);
        form.append("lng", location.lng);
      }
      if (currentLandmarkId) form.append("landmark_id", currentLandmarkId);

      const res = await axios.post(`${API}/chat`, form);
      setMessages(prev => [...prev, { role: "bot", text: res.data.reply, landmark: res.data.landmark }]);
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "Sorry, connection error. Please try again." }]);
    }
    setLoading(false);
  }

  function handleKey(e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  }

  const quickQuestions = [
    "Where am I?",
    "Tell me the history",
    "Who built this?",
    "What is special here?",
  ];

  return (
    <>
      {/* Floating Button */}
      <button className="chat-fab" onClick={() => setOpen(!open)}>
        {open ? "✕" : "💬"}
      </button>

      {/* Chat Panel */}
      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <div>
              <div className="chat-header-title">AI Heritage Guide</div>
              <div className="chat-header-sub">Lahore Fort ·</div>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg ${m.role}`}>
                {m.role === "bot" && <div className="chat-avatar">🕌</div>}
                <div className="chat-bubble">
                  {m.landmark && <div className="chat-landmark-tag">📍 {m.landmark}</div>}
                  {m.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="chat-msg bot">
                <div className="chat-avatar">🕌</div>
                <div className="chat-bubble chat-typing">
                  <span /><span /><span />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Quick Questions */}
          <div className="chat-quick">
            {quickQuestions.map(q => (
              <button key={q} className="chat-quick-btn" onClick={() => { setInput(q); }}>
                {q}
              </button>
            ))}
          </div>

          {/* Input */}
          <div className="chat-input-row">
            <textarea
              className="chat-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask about Lahore Fort..."
              rows={1}
            />
            <button className="chat-send" onClick={sendMessage} disabled={loading || !input.trim()}>
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}