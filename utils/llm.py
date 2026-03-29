"""
LLM abstraction layer — uses Groq as the primary provider.
  • Primary model : Mixtral 8x7B  (fast, high quality)
  • Fallback model: LLaMA 3 8B   (if Mixtral quota exceeded)
  • Offline mock  : rule-based responses (no API key needed)

Get a free Groq API key at https://console.groq.com
"""
import json
import requests
from config import GROQ_API_KEY, GROQ_BASE_URL, GROQ_MIXTRAL, GROQ_LLAMA


def generate_response(
    prompt: str,
    model: str = "mixtral",   # "mixtral" | "llama" | "primary" | "fallback"
    system: str = None,
    max_tokens: int = 1024,
) -> str:
    """
    Universal LLM interface.
    Routes to Groq if GROQ_API_KEY is set, otherwise uses offline mock.
    """
    if GROQ_API_KEY:
        return _groq_generate(prompt, model, system, max_tokens)
    return _mock_generate(prompt, system)


def _groq_generate(
    prompt: str,
    model: str,
    system: str = None,
    max_tokens: int = 1024,
) -> str:
    """Call the Groq chat completions endpoint."""
    # Resolve alias → Groq model ID
    if model in ("mixtral", "primary"):
        model_id = GROQ_MIXTRAL         # mixtral-8x7b-32768
    elif model in ("llama", "fallback"):
        model_id = GROQ_LLAMA           # llama3-8b-8192
    else:
        model_id = model                # allow raw Groq model string

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            GROQ_BASE_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_id,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": 0.7,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.HTTPError as e:
        status = getattr(e.response, "status_code", 0)
        # Rate-limited or model error — retry once with LLaMA fallback
        if status in (429, 503) and model_id != GROQ_LLAMA:
            print(f"[Groq] {e} — retrying with LLaMA fallback")
            return _groq_generate(prompt, "llama", system, max_tokens)
        print(f"[Groq error {status}] {e} — using mock")
        return _mock_generate(prompt, system)

    except Exception as e:
        print(f"[Groq error] {e} — using mock")
        return _mock_generate(prompt, system)


def _mock_generate(prompt: str, system: str = None) -> str:
    """
    Rule-based offline mock — works with zero API keys.
    Returns context-appropriate canned responses.
    """
    p = prompt.lower()

    if "conflict" in p or "resolve" in p:
        return (
            "After analyzing the agent scores, I detect a moderate conflict between water availability "
            "and crop water needs. The water constraint can be partially resolved by adopting drip "
            "irrigation or selecting drought-tolerant varieties. I recommend proceeding with conditional "
            "crops while providing alternatives that have lower water dependency."
        )
    elif "recommend" in p or "option" in p:
        return (
            "Based on the soil profile, climate, market conditions, and farmer constraints, "
            "the recommended crops balance risk and reward. The safe option prioritizes stable income, "
            "the high-reward option targets better market prices with manageable risk, "
            "and the soil health option ensures long-term land productivity through nutrient cycling."
        )
    elif "follow-up" in p or "clarif" in p or ("question" in p and "ask" in p):
        import random
        return random.choice([
            "How reliable is your irrigation source during peak summer months?",
            "Have you faced any recurring pest issues in the past two seasons?",
            "Are you open to trying intercropping or mixed farming this season?",
            "Do you have access to cold storage or a guaranteed buyer for your produce?",
            "What is your preferred crop cycle — short (60–90 days) or long-term?",
        ])
    elif "pest" in p or "disease" in p:
        return (
            "Monitor fields twice weekly. Install yellow sticky traps for whitefly detection. "
            "Consider neem-based sprays as a preventive measure. Watch for early symptoms of fungal "
            "diseases, especially during humid post-rain periods."
        )
    elif "subsidy" in p or "scheme" in p or "insurance" in p:
        return (
            "PM-KISAN provides ₹6,000 annually. Crop insurance under PMFBY at 2% premium for Kharif "
            "and 1.5% for Rabi. Check with your district agriculture office for applicable schemes."
        )
    elif "market" in p or "price" in p or "msp" in p:
        return (
            "Current market conditions are favorable for pulses and oilseeds. "
            "Turmeric and spice crops show strong export demand. "
            "Vegetables have high price volatility — consider contract farming if available."
        )
    elif "greet" in p or "namaste" in p or "hello" in p:
        return (
            "Namaste! I'm Digital Sarathi, your AI farming advisor. "
            "Tell me about your land and what crops you're planning this season — "
            "I'll help you make the best decision."
        )
    else:
        return (
            "As your Digital Sarathi, I'm analyzing your farm profile, soil conditions, water "
            "availability, market trends, and government schemes to give you the best crop "
            "recommendations. Please ensure your profile is complete for more accurate advice."
        )


def generate_json_response(
    prompt: str,
    schema_hint: str = "",
    model: str = "mixtral",
) -> dict:
    """Generate a response and parse it as JSON."""
    json_prompt = (
        f"{prompt}\n\n"
        "Respond ONLY with valid JSON. No explanation, no markdown fences. "
        "Just the raw JSON object."
    )
    if schema_hint:
        json_prompt += f"\n\nExpected schema: {schema_hint}"

    raw = generate_response(json_prompt, model=model)

    try:
        clean = raw.strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[1] if len(parts) > 1 else clean
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean.strip())
    except json.JSONDecodeError:
        return {}
