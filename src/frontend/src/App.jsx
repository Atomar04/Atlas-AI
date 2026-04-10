import { useEffect, useMemo, useState } from "react";
import ChatPanel from "./components/ChatPanel";
import InputBar from "./components/InputBar";
import ResultsList from "./components/ResultsList";
import MapView from "./components/MapView";
import { sendChatQuery } from "./services/api";
import speak from "./hooks/useTextToSpeech";

function getOrCreateSessionId() {
  const key = "atlas_session_id";
  let value = sessionStorage.getItem(key);

  if (!value) {
    value = `session_${crypto.randomUUID()}`;
    sessionStorage.setItem(key, value);
  }

  return value;
}

function normalizeResponse(data) {
  return {
    query: data?.query || "",
    center: data?.center || null,
    places: Array.isArray(data?.places) ? data.places : [],
    summary: data?.summary || "",
    mapActions: data?.map_actions || {},
    interactionHints: Array.isArray(data?.interaction_hints) ? data.interaction_hints : [],
    context: data?.context || {}
  };
}

export default function App() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [places, setPlaces] = useState([]);
  const [selected, setSelected] = useState(null);
  const [center, setCenter] = useState({
    lat: 28.36,
    lng: 75.58
  });
  const [mapZoom, setMapZoom] = useState(13);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setSessionId(getOrCreateSessionId());
  }, []);

  const resultCountText = useMemo(() => {
    if (!places.length) return "No results yet";
    if (places.length === 1) return "1 place found";
    return `${places.length} places found`;
  }, [places]);

  const send = async (query) => {
    const trimmed = query.trim();
    if (!trimmed || !sessionId) return;

    const userMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text: trimmed
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError("");

    try {
      const raw = await sendChatQuery({
        query: trimmed,
        sessionId
      });

      const data = normalizeResponse(raw);

      setPlaces(data.places);
      if (data.center?.lat && data.center?.lng) {
        setCenter(data.center);
      }

      setMapZoom(data.mapActions?.zoom || 14);
      setSelected(data.places?.[0] || null);

      if (data.summary) {
        const assistantMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          text: data.summary,
          hints: data.interactionHints
        };

        setMessages((prev) => [...prev, assistantMessage]);
        speak(data.summary);
      }
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong while contacting the backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <header className="app-topbar">
        <div>
          <div className="brand-title">Atlas AI</div>
          <div className="brand-subtitle">
            Ask the map. Refine naturally. See ranked places live.
          </div>
        </div>

        <div className="topbar-stats">
          <div className="stat-pill">{resultCountText}</div>
          <div className="stat-pill">Session active</div>
        </div>
      </header>

      <div className="layout">
        <aside className="left">
          <ChatPanel messages={messages} loading={loading} error={error} />
          <InputBar onSend={send} disabled={loading} />
        </aside>

        <main className="center">
          <MapView
            center={center}
            places={places}
            selected={selected}
            zoom={mapZoom}
            onSelect={setSelected}
          />
        </main>

        <aside className="right">
          <ResultsList
            places={places}
            selected={selected}
            onSelect={setSelected}
            onAskFollowup={send}
          />
        </aside>
      </div>
    </div>
  );
}