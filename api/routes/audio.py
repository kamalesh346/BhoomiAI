"""
FastAPI routes for cloud-based audio transcription and synthesis.
"""
import os
import tempfile
import base64
from fastapi import APIRouter, UploadFile, File, Response, HTTPException
from api.utils.stt import transcribe_audio
from api.utils.tts import generate_speech
from pydantic import BaseModel

router = APIRouter()

class SynthesisRequest(BaseModel):
    text: str
    language: str = "en"
    voice: str = "default"

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    Local STT endpoint (Faster-Whisper).
    """
    ext = os.path.splitext(file.filename)[1] or ".webm"
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        text = transcribe_audio(tmp_path)
        return {"text": text}
    except Exception as e:
        print(f"Transcribe Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/synthesize")
async def synthesize(req: SynthesisRequest):
    """
    Cloud TTS endpoint (OpenAI). Returns the audio as binary.
    """
    try:
        # generate_speech returns a base64 string like "data:audio/mpeg;base64,..."
        b64_data = generate_speech(req.text, req.language)
        if not b64_data:
            raise ValueError("TTS failed to generate audio")
            
        # Extract raw base64
        header, encoded = b64_data.split(",", 1)
        audio_content = base64.b64decode(encoded)
        
        # OpenAI uses MP3 by default
        return Response(content=audio_content, media_type="audio/mpeg")
    except Exception as e:
        print(f"Synthesize Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
