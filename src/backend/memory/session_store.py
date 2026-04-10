# Simple in-memory session store (can upgrade to Redis later)

SESSION_DB = {}

def get_session(session_id: str):
    return SESSION_DB.get(session_id, {})


def update_session(session_id: str, data: dict):
    """
    Updates or creates session state
    """
    SESSION_DB[session_id] = data