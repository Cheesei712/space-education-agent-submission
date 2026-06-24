import { useState, useRef, useEffect } from 'react';
import { Send, Orbit, Compass } from 'lucide-react';

interface Message {
  sender: 'user' | 'bot';
  text: string;
  target?: string;
  url?: string;
  timestamp: Date;
}

const QUICK_SUGGESTIONS = [
  "Show me Mars!",
  "Tell me about the Voyager 1 spacecraft",
  "What is the Astronomy Picture of the Day?",
  "Are there any close asteroids today?",
  "Explore Jupiter and its moons",
  "Is there any space weather or solar flares?"
];

// Mapping for clean display names from Eyes key
const DISPLAY_NAMES: Record<string, string> = {
  "mercury": "Mercury",
  "venus": "Venus",
  "earth": "Earth",
  "mars": "Mars",
  "jupiter": "Jupiter",
  "saturn": "Saturn",
  "uranus": "Uranus",
  "neptune": "Neptune",
  "pluto": "Pluto",
  "sc_voyager_1": "Voyager 1",
  "sc_voyager_2": "Voyager 2",
  "sc_cassini": "Cassini",
  "sc_new_horizons": "New Horizons",
  "sc_perseverance": "Perseverance Rover",
  "sc_curiosity": "Curiosity Rover",
  "sc_hubble": "Hubble Space Telescope",
  "sc_jwst": "James Webb Space Telescope"
};

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'bot',
      text: "Welcome to StellarAcademy! 🌟 I am your AI Astronomy Educator. I have access to real-time NASA data on planets, spacecrafts, solar flares, and asteroids. Ask me anything about space to explore! 🛰️",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTarget, setActiveTarget] = useState('Solar System Orrery');
  const [iframeUrl, setIframeUrl] = useState('https://eyes.nasa.gov/apps/solar-system/');

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      sender: 'user',
      text: text.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Compute backend API URL dynamically (defaulting to local port 8000 if dev)
    const apiHost = window.location.port === '3000' || window.location.port === '5173'
      ? `${window.location.protocol}//${window.location.hostname}:8000`
      : '';

    try {
      const response = await fetch(`${apiHost}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text.trim() })
      });

      if (!response.ok) {
        throw new Error(`API returned error status: ${response.status}`);
      }

      const data = await response.json();
      
      const botMessage: Message = {
        sender: 'bot',
        text: data.educational_response,
        target: data.simulation_target,
        url: data.simulation_url,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      if (data.simulation_url) {
        setIframeUrl(data.simulation_url);
        const name = DISPLAY_NAMES[data.simulation_target] || data.simulation_target;
        setActiveTarget(name);
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: "I'm having trouble connecting to the launchpad (API error). Please verify that the backend services are running and your Gemini API key is configured.",
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input);
  };

  const syncSimulation = (target: string, url: string) => {
    setIframeUrl(url);
    const name = DISPLAY_NAMES[target] || target;
    setActiveTarget(name);
  };

  return (
    <div className="app-container">
      {/* LEFT PANEL: Chat Dashboard */}
      <div className="sidebar-panel glass-panel">
        <div className="sidebar-header">
          <h1>
            <Orbit className="text-glow animate-pulse" size={24} style={{ color: 'var(--accent-purple)' }} />
            <span className="text-glow font-bold">StellarAcademy</span>
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Astronomy AI Educator & NASA Simulator
          </p>
        </div>

        {/* Messages */}
        <div className="messages-container">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message-bubble ${msg.sender === 'user' ? 'message-user' : 'message-bot'}`}
            >
              <div>{msg.text}</div>
              
              {/* Highlight target synchronizer */}
              {msg.sender === 'bot' && msg.target && msg.url && (
                <div 
                  className="target-badge"
                  onClick={() => syncSimulation(msg.target!, msg.url!)}
                  title="Click to focus the 3D Orrery simulation on this object"
                >
                  <Compass size={12} />
                  Focus Simulation on: {DISPLAY_NAMES[msg.target] || msg.target}
                </div>
              )}

              <div className="message-meta">
                <span>{msg.sender === 'user' ? 'Student' : 'Educator Agent'}</span>
                <span>{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="message-bubble message-bot">
              <div className="typing-indicator">
                TRANSMITTING DATA FROM MISSION CONTROL
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Quick Suggestion Pills */}
        <div className="suggestions-container">
          {QUICK_SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              className="suggestion-pill"
              onClick={() => handleSend(s)}
              disabled={loading}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Chat input form */}
        <form onSubmit={handleFormSubmit} className="input-form">
          <input
            type="text"
            className="glass-input"
            style={{ flex: 1 }}
            placeholder="Ask about planets, stars, spacecraft..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" className="send-button" disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>

      {/* RIGHT PANEL: 3D Solar System Simulation */}
      <div className="simulation-container">
        <iframe
          className="simulation-iframe"
          src={iframeUrl}
          title="NASA's Eyes 3D Solar System Simulation"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>

        {/* Interactive simulation info HUD */}
        <div className="simulation-overlay glass-panel">
          <span className="simulation-overlay-title">Telemetry Focus</span>
          <span className="simulation-overlay-value">{activeTarget}</span>
        </div>
      </div>
    </div>
  );
}
