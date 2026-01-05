import uuid
from fastapi import Request

def get_or_create_session_id(request: Request) -> str:
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
    return session_id