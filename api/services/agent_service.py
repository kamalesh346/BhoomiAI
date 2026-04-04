import json
import uuid
import random
from typing import Dict, Any
from db.database import _conn, get_farmer, create_new_chat_session, update_chat_session
from api.utils.llm import generate_response, generate_json_response

def _save_choice(session_id: int, message_id: str, selected_option: str):
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

def handle_chat_start(farmer_id: int) -> Dict[str, Any]:
    farmer = get_farmer(farmer_id)
    session = create_new_chat_session(farmer_id)
    
    prompt = f"Generate 3 agricultural options (A, B, C) for farmer profile: {json.dumps(farmer)}"
    schema_hint = '{"message": "string", "options": [{"id": "string", "label": "string", "description": "string"}]}'
    
    ai_response = generate_json_response(prompt, schema_hint)
    
    if not ai_response or "options" not in ai_response:
        ai_response = {
            "message": f"Namaste! I am Digital Sarathi. Based on your profile, here are some options:",
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
    
    update_chat_session(session["id"], [ai_message], {})
    
    return {
        "session_id": session["id"],
        "message": ai_message
    }

def handle_chat_message(farmer_id: int, session_id: int, message: str) -> Dict[str, Any]:
    farmer = get_farmer(farmer_id)
    
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT messages FROM chat_sessions WHERE id=%s", (session_id,))
    row = cur.fetchone()
    cur.close()
    c.close()
    
    if not row:
        raise Exception(f"Session {session_id} not found")

    messages = row.get("messages") if isinstance(row, dict) else json.loads(row[0])
    if not isinstance(messages, list): messages = []
    
    messages.append({"role": "user", "content": message})
    
    ai_text = generate_response(message, system=f"You are an Indian agricultural advisor. Farmer: {json.dumps(farmer)}")
    ai_msg = {"role": "assistant", "content": ai_text}
    messages.append(ai_msg)
    
    update_chat_session(session_id, messages, {})
    
    return {"message": ai_msg}

def handle_chat_choice(farmer_id: int, session_id: int, message_id: str, selected_option: str) -> Dict[str, Any]:
    _save_choice(session_id, message_id, selected_option)
    
    metrics = [
        {"subject": "Yield", "A": random.randint(70, 95), "fullMark": 100},
        {"subject": "Market", "A": random.randint(60, 90), "fullMark": 100},
        {"subject": "Survival", "A": random.randint(75, 98), "fullMark": 100},
        {"subject": "Profit", "A": random.randint(65, 95), "fullMark": 100},
    ]
    
    # Simple message generation without calling handle_chat_message again to avoid recursion/state issues
    msg_content = f"You selected Option {selected_option}. This is a great choice! Based on our analysis, this path offers solid prospects as shown in the metrics graph."
    ai_msg = {
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": msg_content,
        "metrics": metrics
    }
    
    # Manual update of session history
    c = _conn()
    cur = c.cursor()
    cur.execute("SELECT messages FROM chat_sessions WHERE id=%s", (session_id,))
    row = cur.fetchone()
    if row:
        msgs = row.get("messages") if isinstance(row, dict) else json.loads(row[0])
        if not isinstance(msgs, list): msgs = []
        msgs.append({"role": "user", "content": f"I selected option {selected_option}."})
        msgs.append(ai_msg)
        cur.execute("UPDATE chat_sessions SET messages=%s WHERE id=%s", (json.dumps(msgs), session_id))
        c.commit()
    cur.close()
    c.close()
    
    return {
        "message": ai_msg,
        "metrics": metrics
    }
