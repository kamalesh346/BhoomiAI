"""
Consultant Mode: Interactive agricultural advisor with dynamic questioning.
"""
import json
from typing import List, Dict, Any
from utils.llm import generate_response
from rag.retriever import retrieve_relevant_info


SYSTEM_PROMPT = """You are Digital Sarathi, an expert Indian agricultural consultant with deep knowledge of:
- Indian crops, seasons, and farming practices
- Government schemes (PM-KISAN, PMFBY, MSP, PMKSY)
- Soil health, water management, IPM
- Market intelligence and crop economics

You are conversing with a farmer. Your style:
- Simple, practical, empathetic
- Ask ONE focused follow-up question at a time
- Give concrete advice grounded in Indian context
- Never give generic advice; always personalize based on what you know about them
- When unsure, ask a clarifying question rather than guessing

Farmer Context: {farmer_context}
"""


def _build_farmer_context(farmer_profile: Dict) -> str:
    """Summarize farmer profile for LLM context."""
    return (
        f"Name: {farmer_profile.get('name', 'Farmer')}, "
        f"Location: {farmer_profile.get('location', 'Unknown')}, "
        f"Land: {farmer_profile.get('land_size', 1)} ha, "
        f"Water: {farmer_profile.get('water_source', 'Unknown')}, "
        f"Budget: ₹{farmer_profile.get('budget', 50000)}, "
        f"Risk: {farmer_profile.get('risk_level', 'medium')}, "
        f"Soil: {farmer_profile.get('soil_type', 'Unknown')}"
    )


def get_initial_greeting(farmer_profile: Dict) -> str:
    """Generate personalized greeting for consultant mode."""
    name = farmer_profile.get("name", "there")
    location = farmer_profile.get("location", "")
    seasons = farmer_profile.get("current_seasons", ["this season"])

    prompt = f"""Generate a warm, personalized greeting as Digital Sarathi for farmer {name} from {location}.
It's {seasons[0] if seasons else 'this'} season. Ask them one specific, practical question about their farming plans.
Keep it under 3 sentences. Be friendly and specific, not generic."""

    return generate_response(prompt, model="mixtral", max_tokens=150)


def generate_consultant_reply(
    user_message: str,
    conversation_history: List[Dict],
    farmer_profile: Dict,
    context: Dict = None
) -> Dict[str, Any]:
    """
    Generate a context-aware consultant reply.
    Returns dict with: message, follow_up_question, rag_context
    """
    context = context or {}
    farmer_ctx = _build_farmer_context(farmer_profile)

    # Retrieve RAG context if relevant
    rag_context = ""
    keywords = ["subsidy", "scheme", "insurance", "loan", "credit", "pest", "disease",
                 "irrigation", "water", "soil", "market", "price", "msp"]
    if any(kw in user_message.lower() for kw in keywords):
        rag_context = retrieve_relevant_info(user_message, k=2)

    # Build conversation messages for LLM
    sys_prompt = SYSTEM_PROMPT.format(farmer_context=farmer_ctx)

    # Construct message history
    messages_text = ""
    for msg in conversation_history[-6:]:  # last 6 turns
        role = "Farmer" if msg["role"] == "user" else "Digital Sarathi"
        messages_text += f"{role}: {msg['content']}\n"

    if rag_context:
        messages_text += f"\n[Relevant Knowledge Base Info]:\n{rag_context[:500]}\n"

    messages_text += f"\nFarmer: {user_message}\nDigital Sarathi:"

    full_prompt = f"{sys_prompt}\n\nConversation:\n{messages_text}"

    response = generate_response(full_prompt, model="mixtral", max_tokens=300)

    # Determine if a follow-up question is embedded
    has_question = "?" in response

    return {
        "message": response.strip(),
        "has_follow_up": has_question,
        "rag_used": bool(rag_context),
        "context_updated": context
    }


def generate_contextual_question(
    topic: str,
    farmer_profile: Dict,
    already_asked: List[str] = None
) -> str:
    """
    Generate a targeted follow-up question about a specific topic.
    Avoids repeating already-asked questions.
    """
    asked = already_asked or []
    name = farmer_profile.get("name", "")

    prompt = f"""As Digital Sarathi, generate ONE specific follow-up question for farmer {name}.
Topic: {topic}
Farmer profile: {_build_farmer_context(farmer_profile)}
Previously asked questions to avoid repeating: {asked}

Rules:
- Ask about something practical and actionable
- Be specific, not vague
- One question only, under 20 words
- Natural, conversational tone"""

    return generate_response(prompt, model="mixtral", max_tokens=80)


def analyze_farmer_needs(conversation_history: List[Dict], farmer_profile: Dict) -> Dict:
    """
    Analyze conversation to extract key needs and concerns.
    Returns structured insights.
    """
    if not conversation_history:
        return {}

    conversation_text = "\n".join([
        f"{m['role'].capitalize()}: {m['content']}"
        for m in conversation_history[-10:]
    ])

    prompt = f"""Based on this conversation with farmer {farmer_profile.get('name', '')},
identify their key concerns, priorities, and constraints.

Conversation:
{conversation_text}

Respond in JSON with keys: main_concern, water_situation, budget_concern, crop_preference, additional_constraints.
Each value should be a short string or null."""

    from utils.llm import generate_json_response
    result = generate_json_response(prompt, model="mixtral")
    return result or {}
