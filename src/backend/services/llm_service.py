import requests
from src.backend.config import OPENROUTER_API_KEY, OPENROUTER_URL, MODEL_NAME


def call_llm(messages):
    """
    Generic LLM caller via OpenRouter
    """
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": 0.2
        }
    )

    if response.status_code != 200:
        return {"error": "LLM call failed"}

    return response.json()["choices"][0]["message"]["content"]