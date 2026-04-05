import json
import uuid
import random
from api.agents.state import AgentState
from api.utils.llm import generate_response, generate_json_response
from db.database import get_farmer, get_pest_history, _conn
from api.agents.specialized_agents import orchestrator_score_crops

def entry_node(state: AgentState) -> dict:
    farmer_id = state["farmer_id"]
    session_id = state.get("session_id")
    
    # Fetch farmer profile
    farmer = get_farmer(farmer_id)
    pest_history = get_pest_history(farmer_id)
    
    past_summary = state.get("past_summary", "")
    past_choices = []
    
    # Fetch past summary & choices if session exists
    if session_id:
        c = _conn()
        cur = c.cursor()
        cur.execute("SELECT summary FROM chat_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone()
        if row and row.get("summary"):
            past_summary = row["summary"]
        
        cur.execute("SELECT * FROM chat_choices WHERE chat_session_id=%s ORDER BY created_at ASC", (session_id,))
        choices = cur.fetchall()
        if choices:
            for c_row in choices:
                for k, v in c_row.items():
                    if hasattr(v, 'isoformat'):
                        c_row[k] = v.isoformat()
            past_choices = list(choices)
        cur.close()
        c.close()
        
    # Detect if user message implies a constraint change (Phase 4)
    constraint_change = False
    if state.get("user_input"):
        prompt = f"Does this user message imply a change in their farming constraints (e.g. new equipment, more budget, different water source)? Message: '{state['user_input']}'"
        res = generate_json_response(prompt, '{"change_detected": boolean, "reason": "string"}')
        if res.get("change_detected"):
            constraint_change = True

    return {
        "farmer_profile": farmer,
        "pest_history": pest_history,
        "past_summary": past_summary,
        "past_choices": past_choices,
        "rerun_required": constraint_change
    }

def recommendation_node(state: AgentState) -> dict:
    farmer = state["farmer_profile"]
    pest_history = state["pest_history"]
    
    # Run the 8-Agent Orchestrator (Phase 1 & 2 logic)
    scored_crops = orchestrator_score_crops(farmer, pest_history)
    
    # Save Top 15-20 to state as cache
    viable_candidates = scored_crops[:20]
    
    # Take Top 3 for immediate presentation
    top_3 = viable_candidates[:3]
    
    options = []
    for i, crop in enumerate(top_3):
        label = f"{crop['name']} (Score: {int(crop['potential_score']*100)}%)"
        desc = f"Suitability based on soil and climate. "
        if crop["required_setup"]:
            desc += f"Requires {crop['required_setup']} for maximum yield."
        if crop["warnings"]:
            desc += f" Note: {crop['warnings'][0]}"
            
        options.append({
            "id": chr(65 + i), # A, B, C
            "label": label,
            "description": desc,
            "crop_data": crop
        })
    
    prompt = (
        f"You are Digital Sarathi. An Indian agricultural expert. "
        f"Present these 3 options to farmer {farmer.get('name')}. "
        f"Highlight why they were chosen and mention any required setups (like Drip Irrigation) or subsidies. "
        f"Options: {json.dumps(options)}"
    )
    
    ai_text = generate_response(prompt, system="Be encouraging and expert. Keep it professional and empathetic.")
    
    ai_message = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": ai_text,
        "options": options
    }
    
    messages = state["messages"].copy()
    messages.append(ai_message)
    
    return {
        "messages": messages, 
        "ai_response": ai_message,
        "viable_candidates": viable_candidates,
        "candidate_crops": scored_crops
    }

def decision_node(state: AgentState) -> dict:
    session_id = state["session_id"]
    message_id = state["message_id"]
    selected_option = state["selected_option"]
    
    try:
        c = _conn()
        cur = c.cursor()
        cur.execute(
            "INSERT INTO chat_choices (chat_session_id, message_id, selected_option) VALUES (%s, %s, %s)",
            (session_id, message_id, selected_option)
        )
        c.commit()
        cur.close()
        c.close()
    except Exception as e:
        print(f"Error saving choice: {e}")
        
    # generate dynamic metrics based on the selected candidate
    metrics = [
        {"subject": "Yield", "A": random.randint(70, 95), "fullMark": 100},
        {"subject": "Market", "A": random.randint(60, 90), "fullMark": 100},
        {"subject": "Sustainability", "A": random.randint(75, 98), "fullMark": 100},
        {"subject": "Profit", "A": random.randint(65, 95), "fullMark": 100},
    ]
    
    messages = state["messages"].copy()
    messages.append({"role": "user", "content": f"I selected option {selected_option}."})
    
    return {"metrics": metrics, "messages": messages}

def reasoning_node(state: AgentState) -> dict:
    farmer = state["farmer_profile"]
    summary = state["past_summary"]
    choices = state["past_choices"]
    messages = state["messages"].copy()
    viable_candidates = state.get("viable_candidates", [])
    
    user_input = state.get("user_input") or ""
    
    # Logic for "Show me more" (Phase 3)
    is_asking_for_more = False
    if user_input:
        is_asking_for_more = any(phrase in user_input.lower() for phrase in ["other", "more", "different", "satisfied", "alternatives"])
    
    if is_asking_for_more and len(viable_candidates) > 3:
        # Fetch next 3 from cache
        next_3 = viable_candidates[3:6]
        options = []
        for i, crop in enumerate(next_3):
            options.append({
                "id": chr(65 + i),
                "label": f"{crop['name']}",
                "description": f"Alternative option with potential score of {int(crop['potential_score']*100)}%"
            })
            
        ai_text = f"I understand! Here are 3 other excellent options from my analysis that also fit your profile:"
        ai_msg = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": ai_text,
            "options": options
        }
        messages.append({"role": "user", "content": user_input})
        messages.append(ai_msg)
        return {"messages": messages, "ai_response": ai_msg}

    if state["selected_option"]:
        system_prompt = (
            f"You are an Indian agricultural advisor. Farmer: {json.dumps(farmer)}. "
            f"Past context: {summary}. "
            f"The user just selected option {state['selected_option']}. "
            "Acknowledge the choice, provide a detailed success plan including any required setups (Drip Irrigation, etc.) and subsidies mentioned in the options."
        )
        message_to_send = f"I selected option {state['selected_option']}."
    else:
        messages.append({"role": "user", "content": user_input})
        system_prompt = (
            f"You are an Indian agricultural advisor. Farmer: {json.dumps(farmer)}. "
            f"Past context: {summary}. "
            f"Past choices: {json.dumps(choices)}. "
            "Provide helpful, concise agricultural advice tailored to the farmer's query and their farm's specifics (water, soil, budget, pest history)."
        )
        message_to_send = user_input

    context_msgs = [m["content"] for m in messages[-5:] if "content" in m]
    full_prompt = "Recent chat history:\n" + "\n".join(context_msgs) + f"\n\nCurrent message: {message_to_send}"
    
    ai_text = generate_response(full_prompt, system=system_prompt)
    
    ai_msg = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": ai_text
    }
    
    if state.get("metrics"):
        ai_msg["metrics"] = state["metrics"]
        
    messages.append(ai_msg)
    return {"messages": messages, "ai_response": ai_msg}

def memory_node(state: AgentState) -> dict:
    messages = state["messages"]
    past_summary = state["past_summary"]
    
    if len(messages) > 6:
        msgs_to_summarize = messages[:-5]
        recent_msgs = messages[-5:]
        
        if msgs_to_summarize:
            text_to_summarize = "\n".join([f"{m['role']}: {m.get('content', '')}" for m in msgs_to_summarize])
            prompt = f"Summarize the following chat history into a concise context for an agricultural advisor. Keep important details. Past summary: {past_summary}\n\nNew chat to add:\n{text_to_summarize}"
            
            new_summary = generate_response(prompt, system="You are a helpful assistant generating concise summaries.")
            return {"past_summary": new_summary, "messages": recent_msgs}
            
    return {}
