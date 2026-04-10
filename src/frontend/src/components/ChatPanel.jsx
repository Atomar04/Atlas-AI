export default function ChatPanel({ messages }) {
  return (
    <div className="chat-panel">
      {messages.map((m) => (
        <div key={m.id} className={`bubble ${m.role}`}>
          <b>{m.role === "user" ? "You" : "AI"}:</b>
          <div>{m.text}</div>
        </div>
      ))}
    </div>
  );
}