const BASE_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

export async function sendChatQuery({ query, sessionId }) {
  const url = new URL(`${BASE_URL}/query`);
  url.searchParams.set("q", query);
  url.searchParams.set("session_id", sessionId);

  const res = await fetch(url.toString(), {
    method: "GET",
    headers: {
      Accept: "application/json"
    }
  });

  if (!res.ok) {
    throw new Error(`Backend request failed with status ${res.status}`);
  }

  const data = await res.json();

  if (data?.error) {
    throw new Error(data.error);
  }

  return data;
}