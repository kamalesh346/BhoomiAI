import json
from typing import Dict, Any
from db.database import _conn, create_new_chat_session, update_chat_session
from api.agents.graph import agent_graph
from api.agents.state import AgentState

def get_session_state(session_id: int) -> tuple[list, str]:
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT messages, summary FROM chat_sessions WHERE id=%s", (session_id,))
    row = cur.fetchone()
    cur.close()
    c.close()
    if not row:
        raise Exception(f"Session {session_id} not found")
    
    messages = row.get("messages")
    if isinstance(messages, str):
        messages = json.loads(messages)
    if not isinstance(messages, list):
        messages = []
        
    summary = row.get("summary", "")
    return messages, summary

def handle_chat_start(farmer_id: int) -> Dict[str, Any]:
    session = create_new_chat_session(farmer_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session["id"],
        farmer_profile={},
        past_summary="",
        past_choices=[],
        messages=[],
        user_input=None,
        selected_option=None,
        message_id=None,
        ai_response=None,
        metrics=None
    )
    
    final_state = agent_graph.invoke(initial_state)
    
    # Save back to DB
    update_chat_session(session["id"], final_state["messages"], {})
    
    return {
        "session_id": session["id"],
        "message": final_state["ai_response"]
    }

def handle_chat_message(farmer_id: int, session_id: int, message: str) -> Dict[str, Any]:
    messages, summary = get_session_state(session_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session_id,
        farmer_profile={},
        past_summary=summary,
        past_choices=[],
        messages=messages,
        user_input=message,
        selected_option=None,
        message_id=None,
        ai_response=None,
        metrics=None
    )
    
    final_state = agent_graph.invoke(initial_state)
    
    # Save to DB
    c = _conn()
    cur = c.cursor()
    cur.execute("UPDATE chat_sessions SET messages=%s, summary=%s WHERE id=%s", 
                (json.dumps(final_state["messages"]), final_state["past_summary"], session_id))
    c.commit()
    cur.close()
    c.close()
    
    return {"message": final_state["ai_response"]}

def handle_chat_choice(farmer_id: int, session_id: int, message_id: str, selected_option: str) -> Dict[str, Any]:
    messages, summary = get_session_state(session_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session_id,
        farmer_profile={},
        past_summary=summary,
        past_choices=[],
        messages=messages,
        user_input=None,
        selected_option=selected_option,
        message_id=message_id,
        ai_response=None,
        metrics=None
    )
    
    final_state = agent_graph.invoke(initial_state)
    
    # Save to DB
    c = _conn()
    cur = c.cursor()
    cur.execute("UPDATE chat_sessions SET messages=%s, summary=%s WHERE id=%s", 
                (json.dumps(final_state["messages"]), final_state["past_summary"], session_id))
    c.commit()
    cur.close()
    c.close()
    
    response = {
        "message": final_state["ai_response"]
    }
    if final_state.get("metrics"):
        response["metrics"] = final_state["metrics"]
    return response
