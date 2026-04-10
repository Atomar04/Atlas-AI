import { useRef, useState } from "react";

export default function useVoiceInput() {
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);

  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition || null;

  const supported = Boolean(SpeechRecognition);

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  };

  const startListening = ({ onResult, onError }) => {
    if (!SpeechRecognition) {
      onError?.("Speech recognition is not supported in this browser.");
      return;
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);

    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };

    recognition.onresult = (event) => {
      const text = event.results?.[0]?.[0]?.transcript || "";
      onResult?.(text);
    };

    recognition.onerror = (e) => {
      const code = e?.error || "unknown_error";
      onError?.(`Voice input error: ${code}`);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  return {
    isListening,
    startListening,
    stopListening,
    supported
  };
}