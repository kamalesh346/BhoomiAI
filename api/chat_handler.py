"""
Central Chat Handler for BhoomiAI.
Implements local multilingual support and voice output.
"""
from api.utils.translator import detect_language, translate_to_english, translate_from_english
from api.utils.tts import generate_speech
from api.services.agent_service import handle_chat_message, handle_chat_start
from typing import Dict, Any

def process_chat_start(farmer_id: int, lang: str = "en") -> Dict[str, Any]:
    """
    Multilingual wrapper for handle_chat_start.
    """
    # 1. Start core English interaction
    response = handle_chat_start(farmer_id)
    
    # 2. Get the assistant's English text
    english_text = response["message"]["content"]
    
    # 3. Translate if needed
    final_lang = lang or "en"
    if final_lang != "en":
        response["message"]["content"] = translate_from_english(english_text, final_lang)
        
    # 4. Generate local speech
    audio = generate_speech(response["message"]["content"], final_lang)
    response["message"]["audio"] = audio
    
    return response

def process_chat_message(farmer_id: int, session_id: int, message: str, lang: str = None) -> Dict[str, Any]:
    """
    Processes chat message through local translation and voice layers.
    """
    # Step 1: Detect language if not provided
    detected_lang = lang or detect_language(message)
    
    # Step 2: Normalize options BEFORE translation (crucial for A/B/C logic)
    normalized_msg = message.lower().strip()
    if normalized_msg in ["a", "option a"]: 
        message = "option a"
    elif normalized_msg in ["b", "option b"]: 
        message = "option b"
    elif normalized_msg in ["c", "option c"]: 
        message = "option c"

    # Step 3: Translate to English if needed (the AI thinks in English)
    english_msg = message
    if detected_lang != "en" and not message.startswith("option "):
        english_msg = translate_to_english(message)

    # Step 4: Call existing agent system (DO NOT MODIFY agent internals)
    # We use handle_chat_message which is already working in the project.
    response = handle_chat_message(farmer_id, session_id, english_msg)

    # Step 5: Translate expert response back to user language
    if detected_lang != "en" and "message" in response:
        original_text = response["message"]["content"]
        translated_text = translate_from_english(original_text, detected_lang)
        response["message"]["content"] = translated_text

    # Step 6: Generate speech (local Piper TTS)
    if "message" in response:
        print(f"[DEBUG] Triggering TTS for: {response['message']['content'][:30]}...")
        audio = generate_speech(response["message"]["content"], detected_lang)
        if audio:
            print(f"[DEBUG] TTS Success: Audio data attached (len: {len(audio)})")
            response["message"]["audio"] = audio
        else:
            print("[DEBUG] TTS Failed: No audio data returned")
    else:
        print("[DEBUG] No message found in response, skipping TTS")

    response["lang"] = detected_lang
    return response
