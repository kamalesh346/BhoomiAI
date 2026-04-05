import json
from typing import Dict, Any
from db.database import _conn, create_new_chat_session, update_chat_session
from api.agents.graph import agent_graph
from api.agents.state import AgentState

def get_session_state(session_id: int) -> tuple[list, str, dict]:
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT messages, summary, context FROM chat_sessions WHERE id=%s", (session_id,))
    row = cur.fetchone()
    cur.close()
    c.close()
    if not row:
        raise Exception(f"Session {session_id} not found")
    
    messages = row.get("messages")
    if isinstance(messages, str):
        try: messages = json.loads(messages)
        except: messages = []
    if not isinstance(messages, list):
        messages = []
        
    summary = row.get("summary", "")
    
    context = row.get("context")
    if isinstance(context, str):
        try: context = json.loads(context)
        except: context = {}
    if not isinstance(context, dict):
        context = {}
        
    return messages, summary, context

def handle_chat_start(farmer_id: int) -> Dict[str, Any]:
    session = create_new_chat_session(farmer_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session["id"],
        farmer_profile={},
        pest_history=[],
        past_summary="",
        past_choices=[],
        messages=[],
        candidate_crops=[],
        viable_candidates=[],
        user_input=None,
        selected_option=None,
        message_id=None,
        ai_response=None,
        metrics=None
    )
    
    final_state = agent_graph.invoke(initial_state)
    
    # Save back to DB including the pre-computed candidates in context
    context = {"viable_candidates": final_state.get("viable_candidates", [])}
    update_chat_session(session["id"], final_state["messages"], context)
    
    return {
        "session_id": session["id"],
        "message": final_state["ai_response"]
    }

def handle_chat_message(farmer_id: int, session_id: int, message: str) -> Dict[str, Any]:
    messages, summary, context = get_session_state(session_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session_id,
        farmer_profile={},
        pest_history=[],
        past_summary=summary,
        past_choices=[],
        messages=messages,
        candidate_crops=[],
        viable_candidates=context.get("viable_candidates", []),
        user_input=message,
        selected_option=None,
        message_id=None,
        ai_response=None,
        metrics=None,
        rerun_required=False
    )
    
    final_state = agent_graph.invoke(initial_state)
    
    # Use update_chat_session for safe serialization and include summary
    new_context = context.copy()
    if final_state.get("viable_candidates"):
        new_context["viable_candidates"] = final_state["viable_candidates"]
    
    update_chat_session(session_id, final_state["messages"], new_context)
    
    # Manually update summary as update_chat_session doesn't handle it
    c = _conn()
    cur = c.cursor()
    cur.execute("UPDATE chat_sessions SET summary=%s WHERE id=%s", (final_state["past_summary"], session_id))
    c.commit()
    cur.close()
    c.close()
    
    return {"message": final_state["ai_response"]}

def handle_chat_choice(farmer_id: int, session_id: int, message_id: str, selected_option: str) -> Dict[str, Any]:
    messages, summary, context = get_session_state(session_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session_id,
        farmer_profile={},
        pest_history=[],
        past_summary=summary,
        past_choices=[],
        messages=messages,
        candidate_crops=[],
        viable_candidates=context.get("viable_candidates", []),
        user_input=None,
        selected_option=selected_option,
        message_id=message_id,
        ai_response=None,
        metrics=None
    )
    
    final_state = agent_graph.invoke(initial_state)
    
    # Use update_chat_session for safe serialization and include summary
    update_chat_session(session_id, final_state["messages"], context)
    
    c = _conn()
    cur = c.cursor()
    cur.execute("UPDATE chat_sessions SET summary=%s WHERE id=%s", (final_state["past_summary"], session_id))
    c.commit()
    cur.close()
    c.close()
    
    response = {
        "message": final_state["ai_response"]
    }
    if final_state.get("metrics"):
        response["metrics"] = final_state["metrics"]
    return response
