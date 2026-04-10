import { useEffect, useRef } from "react";

export default function ChatPanel({ messages, loading, error }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, error]);

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-title">Atlas AI</div>
        <div className="chat-subtitle">
          Conversational place discovery with live map results
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-state-title">Start exploring</div>
            <div className="empty-state-text">
              Try queries like:
              <div className="prompt-list">
                <div>• Best cafes near BITS Pilani</div>
                <div>• Show me hospitals open now in Chennai</div>
                <div>• Only vegetarian ones</div>
                <div>• Which of these is closest?</div>
              </div>
            </div>
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`message-row ${m.role}`}>
            <div className={`bubble ${m.role}`}>
              <div className="bubble-label">
                {m.role === "user" ? "You" : "Atlas"}
              </div>

              <div className="bubble-text">{m.text}</div>

              {m.role === "assistant" && Array.isArray(m.hints) && m.hints.length > 0 && (
                <div className="bubble-hints">
                  {m.hints.map((hint, idx) => (
                    <div key={idx} className="hint-chip">
                      {hint}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-row assistant">
            <div className="bubble assistant">
              <div className="bubble-label">Atlas</div>
              <div className="typing">
                <span />
                <span />
                <span />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="message-row assistant">
            <div className="bubble assistant error-bubble">
              <div className="bubble-label">System</div>
              <div className="bubble-text">{error}</div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  );
}