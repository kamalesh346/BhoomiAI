from api.utils.translator import translate_to_english, translate_from_english
from api.utils.option_parser import normalize_option
from api.services.agent_service import handle_chat_message, handle_chat_choice, handle_chat_start
from typing import Dict, Any

def process_chat_start(farmer_id: int, lang: str = "en") -> Dict[str, Any]:
    """
    Multilingual wrapper for handle_chat_start.
    """
    # 1. Start the core English chat
    response = handle_chat_start(farmer_id)
    
    # 2. Translate initial response if needed
    if lang.lower() != "en" and "message" in response:
        original_text = response["message"]["content"]
        translated_text = translate_from_english(original_text, lang)
        response["message"]["content"] = translated_text
        
    return response

def process_chat_message(farmer_id: int, session_id: int, message: str, lang: str = "en") -> Dict[str, Any]:
    """
    Multilingual wrapper for handle_chat_message.
    Translation happens ONLY at the boundaries.
    """
    print(f"[DEBUG] process_chat_message: lang={lang}, message='{message}'")
    # 1. Normalize structured inputs (e.g. 'Option A') BEFORE translation
    normalized_msg = normalize_option(message)
    
    # 2. Translate user input to English for the core system
    english_msg = normalized_msg
    # Only translate if it's NOT a structured option selection
    if lang.lower() != "en" and not normalized_msg.startswith("option "):
        english_msg = translate_to_english(normalized_msg)
        
    # 3. Call core system (Pure English logic)
    # We check if the normalized message is a direct option selection
    if normalized_msg.startswith("option "):
        option_id = normalized_msg.split(" ")[1].upper() # 'A', 'B', or 'C'
        # To use handle_chat_choice we would need message_id. 
        # For simplicity in this text-based flow, we let the reasoning node handle it via english_msg.
        response = handle_chat_message(farmer_id, session_id, english_msg)
    else:
        response = handle_chat_message(farmer_id, session_id, english_msg)
        
    # 4. Translate expert response back to user language
    if lang.lower() != "en" and "message" in response:
        # We only translate the text content, not metadata/metrics
        original_text = response["message"]["content"]
        translated_text = translate_from_english(original_text, lang)
        response["message"]["content"] = translated_text
        
    return response
