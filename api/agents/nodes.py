import json
import uuid
import random
from api.agents.state import AgentState
from api.utils.llm import generate_response, generate_json_response
from db.database import get_farmer, _conn

def entry_node(state: AgentState) -> dict:
    farmer_id = state["farmer_id"]
    session_id = state.get("session_id")
    
    # Fetch farmer profile
    farmer = get_farmer(farmer_id)
    
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
        
    return {
        "farmer_profile": farmer,
        "past_summary": past_summary,
        "past_choices": past_choices
    }

def recommendation_node(state: AgentState) -> dict:
    farmer = state["farmer_profile"]
    
    prompt = f"Generate 3 agricultural options (A, B, C) for this farmer profile: {json.dumps(farmer)}"
    schema_hint = '{"message": "string", "options": [{"id": "string", "label": "string", "description": "string"}]}'
    
    ai_response = generate_json_response(prompt, schema_hint)
    
    if not ai_response or "options" not in ai_response:
        ai_response = {
            "message": f"Namaste {farmer.get('name', '')}! I am Digital Sarathi. Based on your profile, here are some options:",
            "options": [
                {"id": "A", "label": "Safe Option", "description": "Traditional crop for your area."},
                {"id": "B", "label": "High Yield", "description": "Requires more water but pays better."},
                {"id": "C", "label": "Soil Health", "description": "Legumes to restore soil nutrients."}
            ]
        }
        
    ai_message = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": ai_response["message"],
        "options": ai_response["options"]
    }
    
    messages = state["messages"].copy()
    messages.append(ai_message)
    return {"messages": messages, "ai_response": ai_message}

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
        
    # generate random metrics
    metrics = [
        {"subject": "Yield", "A": random.randint(70, 95), "fullMark": 100},
        {"subject": "Market", "A": random.randint(60, 90), "fullMark": 100},
        {"subject": "Survival", "A": random.randint(75, 98), "fullMark": 100},
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
    
    if state["selected_option"]:
        system_prompt = (
            f"You are an Indian agricultural advisor. Farmer: {json.dumps(farmer)}. "
            f"Past context: {summary}. "
            f"The user just selected option {state['selected_option']}. "
            "Acknowledge the choice, encourage them, and analyze its prospects briefly based on their profile."
        )
        message_to_send = f"I selected option {state['selected_option']}."
    else:
        user_msg = state["user_input"]
        messages.append({"role": "user", "content": user_msg})
        
        system_prompt = (
            f"You are an Indian agricultural advisor. Farmer: {json.dumps(farmer)}. "
            f"Past context: {summary}. "
            f"Past choices: {json.dumps(choices)}. "
            "Provide helpful, concise agricultural advice tailored to the farmer's query and their farm's specifics (water, soil, budget)."
        )
        message_to_send = user_msg

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
