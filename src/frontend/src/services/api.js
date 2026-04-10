const BASE_URL = import.meta.env.VITE_BACKEND_URL;

export async function sendChatQuery(payload) {
  const res = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error("Chat API failed");
  }

  return res.json();
}

export async function fetchRoute(payload) {
  const res = await fetch(`${BASE_URL}/route`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error("Route API failed");
  }

  return res.json();
}