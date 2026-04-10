import { useState } from "react";
import useVoiceInput from "../hooks/useVoiceInput";

export default function InputBar({ onSend }) {
  const [text, setText] = useState("");
  const { isListening, startListening } = useVoiceInput();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;

    onSend(text);
    setText("");
  };

  const handleVoice = () => {
    startListening({
      onResult: (t) => onSend(t),
      onError: alert
    });
  };

  return (
    <form onSubmit={handleSubmit} className="input-bar">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask anything..."
      />

      <button type="submit">Send</button>

      <button
        type="button"
        className={isListening ? "listening" : ""}
        onClick={handleVoice}
      >
        {isListening ? "Listening..." : "🎤"}
      </button>
    </form>
  );
}