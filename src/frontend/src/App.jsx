import { useState } from "react";
import ChatPanel from "./components/ChatPanel";
import InputBar from "./components/InputBar";
import ResultsList from "./components/ResultsList";
import MapView from "./components/MapView";
import { sendChatQuery } from "./services/api";
import speak from "./hooks/useTextToSpeech";

let id = 0;

export default function App() {
  const [messages, setMessages] = useState([]);
  const [places, setPlaces] = useState([]);
  const [selected, setSelected] = useState(null);
  const [center, setCenter] = useState({
    lat: 28.36,
    lng: 75.58
  });

  const send = async (query) => {
    setMessages((m) => [...m, { id: ++id, role: "user", text: query }]);

    const data = await sendChatQuery({ query });

    setPlaces(data.places || []);
    setCenter(data.center || center);

    if (data.summary) {
      setMessages((m) => [
        ...m,
        { id: ++id, role: "assistant", text: data.summary }
      ]);

      speak(data.summary);
    }
  };

  return (
    <div className="layout">
      <div className="left">
        <ChatPanel messages={messages} />
        <InputBar onSend={send} />
      </div>

      <div className="center">
        <MapView
          center={center}
          places={places}
          selected={selected}
        />
      </div>

      <div className="right">
        <ResultsList places={places} onSelect={setSelected} />
      </div>
    </div>
  );
}