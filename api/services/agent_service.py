"""
BhoomiAI Agent Service
----------------------
Orchestrates the interaction between the FastAPI routes, the database, 
and the LangGraph-based agent workflow. Handles session persistence and state recovery.
"""

import json
from typing import Dict, Any, List, Tuple
from db.database import _conn, create_new_chat_session, update_chat_session
from api.agents.graph import agent_graph
from api.agents.state import AgentState

def get_session_state(session_id: int) -> Tuple[List, str, Dict, List]:
    """
    Recovers the complete conversation state from the database.
    Returns: (messages, summary, context, past_choices)
    """
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT messages, summary, context FROM chat_sessions WHERE id=%s", (session_id,))
    row = cur.fetchone()
    
    # Fetch structured history of crop selections
    cur.execute("SELECT crop_name FROM chat_choices WHERE chat_session_id=%s ORDER BY created_at ASC", (session_id,))
    choice_rows = cur.fetchall()
    past_choices = [r["crop_name"] for r in choice_rows if r["crop_name"]]
    
    cur.close()
    c.close()
    if not row:
        raise Exception(f"Session {session_id} not found")
    
    # Deserialize messages list
    messages = row.get("messages")
    if isinstance(messages, str):
        try: messages = json.loads(messages)
        except: messages = []
    if not isinstance(messages, list):
        messages = []
        
    summary = row.get("summary", "")
    
    # Deserialize metadata context
    context = row.get("context")
    if isinstance(context, str):
        try: context = json.loads(context)
        except: context = {}
    if not isinstance(context, dict):
        context = {}
        
    return messages, summary, context, past_choices

def handle_chat_start(farmer_id: int) -> Dict[str, Any]:
    """
    Initializes a new BhoomiAI session.
    Triggers the first agent run to generate initial crop recommendations.
    """
    session = create_new_chat_session(farmer_id)
    
    # Initialize blank state for the graph
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
        metrics=None,
        rerun_required=False
    )
    
    # Execute graph logic
    final_state = agent_graph.invoke(initial_state)
    
    # Save results back to DB (caching viable candidates for future pagination/alternatives)
    context = {"viable_candidates": final_state.get("viable_candidates", [])}
    update_chat_session(session["id"], final_state["messages"], context)
    
    return {
        "session_id": session["id"],
        "message": final_state["ai_response"]
    }

def handle_chat_message(farmer_id: int, session_id: int, message: str) -> Dict[str, Any]:
    """
    Processes a user's natural language message through the agent graph.
    Maintains continuity by recovering past summary and context.
    """
    messages, summary, context, past_choices = get_session_state(session_id)
    
    # Reconstruct state from DB
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session_id,
        farmer_profile={},
        pest_history=[],
        past_summary=summary,
        past_choices=past_choices,
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
    
    # Run graph
    final_state = agent_graph.invoke(initial_state)
    
    # Update persistence layers
    new_context = context.copy()
    if final_state.get("viable_candidates"):
        new_context["viable_candidates"] = final_state["viable_candidates"]
    
    update_chat_session(session_id, final_state["messages"], new_context)
    
    # Persist the updated summary separately (Agent logic periodically updates this)
    c = _conn()
    cur = c.cursor()
    cur.execute("UPDATE chat_sessions SET summary=%s WHERE id=%s", (final_state["past_summary"], session_id))
    c.commit()
    cur.close()
    c.close()
    
    return {"message": final_state["ai_response"]}

def handle_chat_choice(farmer_id: int, session_id: int, message_id: str, selected_option: str) -> Dict[str, Any]:
    """
    Specialized handler for option selection (A, B, or C).
    Triggers the decision node to lock in a crop choice.
    """
    messages, summary, context, past_choices = get_session_state(session_id)
    
    initial_state = AgentState(
        farmer_id=farmer_id,
        session_id=session_id,
        farmer_profile={},
        pest_history=[],
        past_summary=summary,
        past_choices=past_choices,
        messages=messages,
        candidate_crops=[],
        viable_candidates=context.get("viable_candidates", []),
        user_input=None,
        selected_option=selected_option,
        message_id=message_id,
        ai_response=None,
        metrics=None,
        rerun_required=False
    )
    
    # Run graph
    final_state = agent_graph.invoke(initial_state)
    
    # Update persistence
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
    # Attach simulation metrics if generated (radar chart data)
    if final_state.get("metrics"):
        response["metrics"] = final_state["metrics"]
    return response
