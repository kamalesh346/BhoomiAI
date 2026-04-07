"""
Local STT Module using Faster-Whisper.
No external API calls — runs fully on local hardware.
"""
import torch
from faster_whisper import WhisperModel
import threading

class LocalSTT:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LocalSTT, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        print("[LocalSTT] Initializing Faster-Whisper (first time only)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load the model (small or base is good for most CPUs)
        # compute_type="int8" is faster on CPU
        self.model = WhisperModel("base", device=self.device, compute_type="int8" if self.device == "cpu" else "float16")
        
        self._initialized = True
        print(f"[LocalSTT] Faster-Whisper loaded on {self.device}")

    def transcribe(self, audio_path: str) -> str:
        """Transcribes audio file and returns text."""
        try:
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            text = " ".join([segment.text for segment in segments])
            return text.strip()
        except Exception as e:
            print(f"[STT Error] {e}")
            raise e

# Singleton
_stt = None

def get_stt():
    global _stt
    if _stt is None:
        _stt = LocalSTT()
    return _stt

def transcribe_audio(audio_path: str) -> str:
    return get_stt().transcribe(audio_path)
