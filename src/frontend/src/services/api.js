const BASE_URL = "/api";

export async function sendChatQuery({ query, sessionId }) {
  const res = await fetch(`${BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      query: query,
      session_id: sessionId,
    }),
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