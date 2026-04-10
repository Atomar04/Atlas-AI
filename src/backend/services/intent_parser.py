import json
from src.backend.services.llm_service import call_llm


SYSTEM_PROMPT = """
You are an AI system that converts user queries into structured JSON.

Extract:
- intent (search_places / refine_results / get_route)
- category
- location
- filters (open_now, veg_only, etc.)
- sort_by (rating, distance, relevance)
- top_k

Rules:
- Always return valid JSON
- No explanation
- If location is not given, use "current_location"
"""


def parse_intent(query: str):

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]

    response = call_llm(messages)

    try:
        return json.loads(response)
    except:
        return {"intent": "unknown"}