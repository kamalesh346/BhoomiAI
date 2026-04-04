from fastapi import APIRouter, HTTPException
from api.db.models import ChatStartRequest, ChatMessageRequest, ChatChoiceRequest
from api.services.agent_service import handle_chat_start, handle_chat_message, handle_chat_choice
from db.database import _conn
import json

router = APIRouter()

@router.post("/start")
def start_chat(req: ChatStartRequest):
    try:
        response = handle_chat_start(req.farmer_id)
        return {"status": "success", **response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
def chat_message(req: ChatMessageRequest):
    try:
        response = handle_chat_message(req.farmer_id, req.chat_session_id, req.message)
        return {"status": "success", **response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/choice")
def chat_choice(req: ChatChoiceRequest):
    try:
        response = handle_chat_choice(req.farmer_id, req.chat_session_id, req.message_id, req.selected_option)
        return {"status": "success", **response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
def get_history(session_id: int):
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT * FROM chat_sessions WHERE id=%s", (session_id,))
    session = cur.fetchone()
    cur.close()
    c.close()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    messages = json.loads(session["messages"]) if session["messages"] else []
    return {
        "status": "success",
        "session_id": session_id,
        "summary": session.get("summary", ""),
        "messages": messages
    }
