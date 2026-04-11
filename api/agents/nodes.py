"""
BhoomiAI Agent Nodes
--------------------
Contains the core logic for each node in the LangGraph workflow.
Processes data fetching, recommendations, decisions, reasoning, and memory.
"""

import json
import uuid
import random
from api.agents.state import AgentState
from api.utils.llm import generate_response, generate_json_response
from db.database import get_farmer, get_pest_history, _conn
from api.agents.specialized_agents import orchestrator_score_crops

def entry_node(state: AgentState) -> dict:
    """
    Initial node for all chat sessions.
    Fetches farmer data and determines if physical constraints have changed.
    """
    farmer_id = state["farmer_id"]
    session_id = state.get("session_id")
    
    # 1. Fetch persistent farmer profile
    farmer = get_farmer(farmer_id)
    pest_history = get_pest_history(farmer_id)
    
    past_summary = state.get("past_summary", "")
    past_choices = []
    
    # 2. Fetch past summary & choices from DB if session exists
    if session_id:
        c = _conn()
        cur = c.cursor()
        cur.execute("SELECT summary FROM chat_sessions WHERE id=%s", (session_id,))
        row = cur.fetchone()
        if row and row.get("summary"):
            past_summary = row["summary"]
        
        # Structured Memory: Fetch previously selected Crop Names
        cur.execute("SELECT crop_name, selected_option FROM chat_choices WHERE chat_session_id=%s ORDER BY created_at ASC", (session_id,))
        choices = cur.fetchall()
        if choices:
            past_choices = [c_row["crop_name"] for c_row in choices if c_row["crop_name"]]
        cur.close()
        c.close()
        
    # 3. Detect Constraint Changes (Phase 4)
    # Checks if the user's latest input implies a major change in physical capability.
    constraint_change = False
    if state.get("user_input"):
        prompt = (
            f"Analyze if this message mentions a change in PHYSICAL farming constraints "
            f"(e.g. new borewell, different budget, new equipment, different water source). "
            f"Do NOT trigger for 'change of mind' or 'selecting an option'. "
            f"Message: '{state['user_input']}'"
        )
        res = generate_json_response(prompt, '{"physical_change_detected": boolean, "reason": "string"}')
        if res.get("physical_change_detected"):
            constraint_change = True

    return {
        "farmer_profile": farmer,
        "pest_history": pest_history,
        "past_summary": past_summary,
        "past_choices": past_choices,
        "rerun_required": constraint_change
    }

def recommendation_node(state: AgentState) -> dict:
    """
    Generates the top 3 crop recommendations using the multi-agent orchestrator.
    Presents these options to the user.
    """
    farmer = state["farmer_profile"]
    pest_history = state["pest_history"]
    
    # 1. Run the Multi-Agent Scorer (8 specialized agents)
    scored_crops = orchestrator_score_crops(farmer, pest_history)
    viable_candidates = scored_crops[:20]
    top_3 = viable_candidates[:3]
    
    # 2. Format options for frontend rendering
    options = []
    for i, crop in enumerate(top_3):
        label = f"{crop['name']} (Score: {int(crop['potential_score']*100)}%)"
        desc = f"Suitability based on soil and climate."
        if crop["required_setup"]:
            desc += f" Needs {crop['required_setup']}."
            
        options.append({
            "id": chr(65 + i), 
            "label": label,
            "description": desc,
            "crop_name": crop["name"],
            "crop_data": crop
        })
    
    # 3. Generate natural language introduction
    system_msg = (
        "You are BhoomiAI. Greet the farmer ONLY if this is the start of the session. "
        "Present 3 crop options (A, B, C) clearly. Explain why they fit the profile briefly. "
        "Maintain a professional, expert, and concise tone. "
        "CRITICAL: ALWAYS respond in English. Final translation is handled externally."
    )
    
    prompt = f"Farmer Profile: {json.dumps(farmer)}\nOptions: {json.dumps(options)}"
    ai_text = generate_response(prompt, system=system_msg)
    
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
    """
    Triggers when a user selects an option (A, B, or C).
    Persists the choice and generates success metrics for visualization.
    """
    session_id = state["session_id"]
    message_id = state["message_id"]
    selected_option = state["selected_option"]
    messages = state["messages"]
    
    # 1. Map option ID back to crop name
    selected_crop_name = "Unknown"
    for msg in reversed(messages):
        if msg.get("id") == message_id and "options" in msg:
            for opt in msg["options"]:
                if opt["id"] == selected_option:
                    selected_crop_name = opt.get("crop_name", selected_option)
                    break
            break
    
    # 2. Persist choice to database
    try:
        c = _conn()
        cur = c.cursor()
        cur.execute(
            "INSERT INTO chat_choices (chat_session_id, message_id, selected_option, crop_name) VALUES (%s, %s, %s, %s)",
            (session_id, message_id, selected_option, selected_crop_name)
        )
        c.commit()
        cur.close()
        c.close()
    except Exception as e:
        print(f"Error saving choice: {e}")
        
    # 3. Generate simulation metrics for the selected crop
    metrics = [
        {"subject": "Yield", "A": random.randint(70, 95), "fullMark": 100},
        {"subject": "Market", "A": random.randint(60, 90), "fullMark": 100},
        {"subject": "Sustainability", "A": random.randint(75, 98), "fullMark": 100},
        {"subject": "Profit", "A": random.randint(65, 95), "fullMark": 100},
    ]
    
    new_messages = messages.copy()
    new_messages.append({"role": "user", "content": f"I selected option {selected_option}: {selected_crop_name}."})
    
    return {"metrics": metrics, "messages": new_messages, "past_choices": state["past_choices"] + [selected_crop_name]}

def reasoning_node(state: AgentState) -> dict:
    """
    Handles ongoing consultation, provides alternative options, 
    and generates detailed agricultural implementation plans.
    """
    farmer = state["farmer_profile"]
    summary = state["past_summary"]
    choices = state.get("past_choices", [])
    messages = state["messages"].copy()
    viable_candidates = state.get("viable_candidates", [])
    user_input = state.get("user_input") or ""
    
    # 1. Check if user is asking for more alternatives
    is_asking_for_more = False
    if user_input:
        is_asking_for_more = any(phrase in user_input.lower() for phrase in ["other options", "show options", "change crop", "more crops", "not satisfied"])
    
    if is_asking_for_more and len(viable_candidates) > 3:
        next_3 = viable_candidates[3:6]
        options = []
        for i, crop in enumerate(next_3):
            options.append({
                "id": chr(65 + i),
                "label": f"{crop['name']}",
                "description": f"Alternative with potential score of {int(crop['potential_score']*100)}%",
                "crop_name": crop["name"]
            })
        ai_msg = {
            "id": str(uuid.uuid4()),
            "role": "assistant",
            "content": "I understand. Here are 3 other suitable options for your consideration:",
            "options": options
        }
        messages.append({"role": "user", "content": user_input})
        messages.append(ai_msg)
        return {"messages": messages, "ai_response": ai_msg}

    # 2. Consultation Logic: Provide detailed plans or answer inquiries
    choices_str = ", ".join(choices) if choices else "No crop selected yet"
    
    system_prompt = (
        "You are BhoomiAI, a stateful agricultural advisor. "
        "RULES:\n"
        "1. Never repeat greetings (Namaste etc.) if the conversation is ongoing.\n"
        "2. If the user refers to 'Option A/B/C', identify it from recent history and LOCK onto that crop.\n"
        "3. Once a crop is selected, provide a plan using these headers:\n"
        "   ✔ Plan\n"
        "   💰 Budget\n"
        "   🌱 Setup\n"
        "   ⚠ Risks\n"
        "4. Do NOT suggest new crops unless explicitly asked or physical constraints changed significantly.\n"
        "5. Be concise and farmer-friendly. "
        "6. CRITICAL: ALWAYS respond in English. Final translation is handled externally."
    )

    history_context = f"Farmer: {json.dumps(farmer)}\nPast Decisions: {choices_str}\nContext Summary: {summary}"
    
    if state.get("selected_option"):
        message_to_send = f"User selected option {state['selected_option']}."
    else:
        messages.append({"role": "user", "content": user_input})
        message_to_send = user_input

    # Optimize prompt context (last 10 messages)
    context_msgs = [m["content"] for m in messages[-10:] if "content" in m]
    full_prompt = f"{history_context}\n\nRecent Chat:\n" + "\n".join(context_msgs) + f"\n\nCurrent Input: {message_to_send}"
    
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
    """
    Compresses long conversations into a structured technical summary.
    Maintains efficiency by pruning old message history while preserving context.
    """
    messages = state["messages"]
    past_summary = state["past_summary"]
    
    # Only summarize when history exceeds 10 turns
    if len(messages) > 10:
        msgs_to_summarize = messages[:-10]
        recent_msgs = messages[-10:]
        
        if msgs_to_summarize:
            text_to_summarize = "\n".join([f"{m['role']}: {m.get('content', '')}" for m in msgs_to_summarize])
            prompt = (
                f"Summarize this interaction for a stateful advisor. Focus on:\n"
                f"- Crops Suggested\n"
                f"- Decisions Made\n"
                f"- Current Goal\n\n"
                f"Past summary: {past_summary}\n\n"
                f"New interactions:\n{text_to_summarize}"
            )
            new_summary = generate_response(prompt, system="Generate a structured, technical agricultural summary.")
            return {"past_summary": new_summary, "messages": recent_msgs}
            
    return {}
