"""
LLM abstraction layer — uses Groq as the primary provider.
"""
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MIXTRAL  = "llama-3.1-8b-instant"
GROQ_LLAMA    = "llama-3.1-8b-instant"

def generate_response(
    prompt: str,
    model: str = "mixtral",
    system: str = None,
    max_tokens: int = 1024,
) -> str:
    if GROQ_API_KEY:
        return _groq_generate(prompt, model, system, max_tokens)
    return _mock_generate(prompt, system)

def _groq_generate(
    prompt: str,
    model: str,
    system: str = None,
    max_tokens: int = 1024,
) -> str:
    if model in ("mixtral", "primary"):
        model_id = GROQ_MIXTRAL
    elif model in ("llama", "fallback"):
        model_id = GROQ_LLAMA
    else:
        model_id = model

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
    except Exception as e:
        print(f"[Groq error] {e} — using mock")
        return _mock_generate(prompt, system)

def _mock_generate(prompt: str, system: str = None) -> str:
    p = prompt.lower()
    if "recommend" in p or "option" in p:
        return "Based on your profile, I recommend pulses or oilseeds for this season."
    elif "greet" in p or "namaste" in p or "hello" in p:
        return "Namaste! I'm BhoomiAI, your AI farming advisor."
    else:
        return "I am analyzing your farm profile to give you the best advice."

def generate_json_response(
    prompt: str,
    schema_hint: str = "",
    model: str = "mixtral",
) -> dict:
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
