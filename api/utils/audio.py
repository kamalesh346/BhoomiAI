"""
Audio utility layer for Speech-to-Text (Whisper) and Text-to-Speech (Orpheus).
Uses Groq Cloud API for both.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_TTS_URL = "https://api.groq.com/openai/v1/audio/speech"

# Whisper model for STT
WHISPER_MODEL = "whisper-large-v3-turbo"

# Orpheus model for TTS (Canopy Labs)
# Note: Ensure the model ID is correct based on Groq's latest documentation.
# Standard Orpheus model ID on Groq is typically 'canopylabs/orpheus-3b-0.1-ft' or similar.
ORPHEUS_MODEL = "canopylabs/orpheus-v1-english"

def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribes audio using Groq's Whisper API.
    """
    if not GROQ_API_KEY:
        return "Speech-to-text is not configured (missing API key)."

    try:
        with open(audio_file_path, "rb") as f:
            files = {
                "file": (os.path.basename(audio_file_path), f),
            }
            data = {
                "model": WHISPER_MODEL,
                "response_format": "json",
                "language": "en" # Or detect from farmer profile
            }
            response = requests.post(
                GROQ_STT_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files=files,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("text", "")
    except Exception as e:
        print(f"[STT Error] {e}")
        # Re-raise to let the route handle the error status code properly
        raise e

import re

def synthesize_speech(text: str, voice: str = "autumn") -> bytes:
    """
    Synthesizes speech using Canopy Labs Orpheus TTS via Groq.
    Handles the 200-character limit by chunking the text.
    Returns the concatenated audio bytes (WAV format).
    """
    if not GROQ_API_KEY:
        raise ValueError("Text-to-speech is not configured (missing API key).")

    # The Orpheus model has a strict ~200 character limit per request.
    # We split by sentence endings while keeping chunks under 200 chars.
    chunks = []
    # Simple regex to split by . ! ? while keeping the delimiter
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < 190:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If a single sentence is > 190, we have to hard split it
            if len(sentence) > 190:
                for i in range(0, len(sentence), 190):
                    chunks.append(sentence[i:i+190])
                current_chunk = ""
            else:
                current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())

    combined_audio = b""
    
    try:
        for chunk in chunks:
            if not chunk: continue
            
            payload = {
                "model": ORPHEUS_MODEL,
                "input": chunk,
                "voice": voice,
                "response_format": "wav",
            }
            response = requests.post(
                GROQ_TTS_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            # For WAV files, the first chunk includes the header. 
            # Subsequent chunks should ideally have their headers stripped if we want a valid single WAV file,
            # but most players (including browser's Audio) are resilient to concatenated WAVs
            # or we can just append the raw data.
            # A more robust way is to strip the 44-byte header from chunks after the first.
            audio_data = response.content
            if combined_audio and len(audio_data) > 44:
                combined_audio += audio_data[44:]
            else:
                combined_audio += audio_data
                
        return combined_audio
    except Exception as e:
        print(f"[TTS Error] {e}")
        raise e
