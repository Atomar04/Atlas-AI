import { useRef, useState } from "react";

export default function useVoiceInput() {
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);

  const startListening = ({ onResult, onError }) => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      onError?.("Speech not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event) => {
      const text = event.results[0][0].transcript;
      onResult(text);
    };

    recognition.onerror = (e) => {
      onError(e.error);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  return { isListening, startListening };
}