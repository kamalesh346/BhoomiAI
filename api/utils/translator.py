from api.utils.llm import generate_response

LANG_MAP = {
    "en": "English",
    "hi": "Hindi",
    "mr": "Marathi",
    "ta": "Tamil",
    "te": "Telugu",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi"
}

def translate_to_english(text: str) -> str:
    """Translates user input from any language to English."""
    if not text or text.strip() == "":
        return text
        
    prompt = f"Translate the following agricultural query into plain English. Respond ONLY with the translation:\n\n{text}"
    translation = generate_response(prompt, system="You are a professional translator. Provide direct, accurate translations.")
    return translation.strip()

def translate_from_english(text: str, target_lang: str) -> str:
    """Translates system response from English to the farmer's target language."""
    if not text or not target_lang or target_lang.lower() == "en":
        return text
    
    full_lang = LANG_MAP.get(target_lang.lower(), target_lang)
        
    prompt = f"Translate the following agricultural advice into {full_lang}. Maintain the tone and all technical details. Respond ONLY with the translation:\n\n{text}"
    translation = generate_response(prompt, system=f"You are a professional translator specialized in {full_lang}. Translate technical farming advice accurately.")
    return translation.strip()
