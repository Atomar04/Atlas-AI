import { useState } from "react";
import useVoiceInput from "../hooks/useVoiceInput";

export default function InputBar({ onSend, disabled }) {
  const [text, setText] = useState("");
  const { isListening, startListening, stopListening, supported } = useVoiceInput();

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = text.trim();
    if (!trimmed || disabled) return;

    onSend(trimmed);
    setText("");
  };

  const handleVoice = () => {
    if (!supported) {
      window.alert("Speech recognition is not supported in this browser.");
      return;
    }

    if (isListening) {
      stopListening();
      return;
    }

    startListening({
      onResult: (spokenText) => {
        const trimmed = spokenText.trim();
        if (!trimmed) return;
        onSend(trimmed);
      },
      onError: (message) => {
        window.alert(message || "Voice input failed.");
      }
    });
  };

  return (
    <form onSubmit={handleSubmit} className="input-bar">
      <input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Ask about places, then refine naturally..."
        disabled={disabled}
      />

      <button type="submit" disabled={disabled || !text.trim()} className="send-btn">
        Send
      </button>

      <button
        type="button"
        className={`voice-btn ${isListening ? "listening" : ""}`}
        onClick={handleVoice}
        disabled={disabled}
        title={supported ? "Use voice input" : "Voice input not supported"}
      >
        {isListening ? "Stop" : "🎤"}
      </button>
    </form>
  );
}