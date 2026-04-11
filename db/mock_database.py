"""
Mock database layer for running BhoomiAI without PostgreSQL.
Useful for demos, testing, or environments without a DB.
Activated automatically when DATABASE_URL is unreachable.
"""
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, List, Any


# ─── In-memory storage ───────────────────────────────────────────────────────
_farmers: Dict[int, dict] = {}
_history: List[dict] = []
_recommendations: List[dict] = []
_chat_sessions: Dict[int, dict] = {}
_email_index: Dict[str, int] = {}
_next_id = {"farmer": 1, "history": 1, "rec": 1, "session": 1}


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def init_mock():
    """Seed mock database with test farmer."""
    global _farmers, _history, _recommendations, _email_index

    if "test@farmer.com" not in _email_index:
        fid = _next_id["farmer"]
        _farmers[fid] = {
            "id": fid, "name": "Raju Patel", "email": "test@farmer.com",
            "password": _hash("test123"), "land_size": 2.5,
            "water_source": "Canal", "budget": 80000, "risk_level": "medium",
            "equipment": json.dumps(["Tractor", "Drip Irrigation"]),
            "location": "Maharashtra", "soil_type": "Black Cotton",
            "npk_n": 75, "npk_p": 35, "npk_k": 45, "soil_ph": 6.8,
            "created_at": datetime.now()
        }
        _email_index["test@farmer.com"] = fid
        _next_id["farmer"] += 1

        # Seed history
        for crop, season, year, yld, inc, notes in [
            ("Cotton", "Kharif", 2023, 1200, 79440, "Good yield"),
            ("Wheat", "Rabi", 2023, 2800, 63420, "Average"),
            ("Soybean", "Kharif", 2022, 900, 41400, "Dry spell"),
            ("Chickpea", "Rabi", 2022, 750, 40800, "Good quality"),
            ("Jowar", "Kharif", 2021, 1500, 41070, "Excellent"),
        ]:
            hid = _next_id["history"]
            _history.append({
                "id": hid, "farmer_id": fid, "crop": crop,
                "season": season, "year": year, "yield_kg": yld,
                "income": inc, "notes": notes, "created_at": datetime.now()
            })
            _next_id["history"] += 1


# ─── Mock CRUD ───────────────────────────────────────────────────────────────

def create_farmer(name, email, password, location="Maharashtra"):
    fid = _next_id["farmer"]
    farmer = {
        "id": fid, "name": name, "email": email,
        "password": _hash(password), "land_size": 1.0,
        "water_source": "Rain-fed", "budget": 50000, "risk_level": "medium",
        "equipment": "[]", "location": location, "soil_type": "Loamy",
        "npk_n": 80, "npk_p": 40, "npk_k": 40, "soil_ph": 6.5,
        "created_at": datetime.now()
    }
    if email in _email_index:
        raise Exception("Email already exists (unique constraint)")
    _farmers[fid] = farmer
    _email_index[email] = fid
    _next_id["farmer"] += 1
    return farmer


def login_farmer(email, password):
    fid = _email_index.get(email)
    if not fid:
        return None
    f = _farmers.get(fid)
    if f and f["password"] == _hash(password):
        return f
    return None


def get_farmer(farmer_id):
    return _farmers.get(farmer_id)


def update_farmer_profile(farmer_id, **kwargs):
    if farmer_id in _farmers:
        _farmers[farmer_id].update(kwargs)


def get_crop_history(farmer_id):
    return [h for h in _history if h["farmer_id"] == farmer_id]


def add_crop_history(farmer_id, crop, season, year, yield_kg=None, income=None, notes=""):
    hid = _next_id["history"]
    _history.append({
        "id": hid, "farmer_id": farmer_id, "crop": crop,
        "season": season, "year": year, "yield_kg": yield_kg,
        "income": income, "notes": notes, "created_at": datetime.now()
    })
    _next_id["history"] += 1


def save_recommendation(farmer_id, option_a, option_b, option_c,
                         explanation, subsidy_info, pest_warnings):
    rid = _next_id["rec"]
    _recommendations.append({
        "id": rid, "farmer_id": farmer_id,
        "option_a": option_a, "option_b": option_b, "option_c": option_c,
        "explanation": explanation, "subsidy_info": subsidy_info,
        "pest_warnings": pest_warnings, "created_at": datetime.now()
    })
    _next_id["rec"] += 1


def get_recommendations(farmer_id, limit=5):
    recs = [r for r in _recommendations if r["farmer_id"] == farmer_id]
    return sorted(recs, key=lambda x: x["created_at"], reverse=True)[:limit]


def create_new_chat_session(farmer_id):
    sid = _next_id["session"]
    _chat_sessions[farmer_id] = {
        "id": sid, "farmer_id": farmer_id,
        "messages": [], "context": {},
        "created_at": datetime.now()
    }
    _next_id["session"] += 1
    return _chat_sessions[farmer_id]


def get_or_create_chat_session(farmer_id):
    if farmer_id not in _chat_sessions:
        sid = _next_id["session"]
        _chat_sessions[farmer_id] = {
            "id": sid, "farmer_id": farmer_id,
            "messages": [], "context": {},
            "created_at": datetime.now()
        }
        _next_id["session"] += 1
    return _chat_sessions[farmer_id]


def update_chat_session(session_id, messages, context):
    for fid, s in _chat_sessions.items():
        if s["id"] == session_id:
            s["messages"] = messages
            s["context"] = context
            break


# Auto-init mock data on import
init_mock()
