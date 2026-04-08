"""
TTS Module using Edge-TTS (Microsoft Azure Neural Voices).
Provides high-quality, free, and multilingual speech synthesis.
"""
import asyncio
import base64

try:
    import edge_tts
except ImportError:
    edge_tts = None


class EdgeTTSProvider:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EdgeTTSProvider, cls).__new__(cls)
        return cls._instance

    async def _generate_async(self, text: str, lang: str):
        if edge_tts is None:
            raise RuntimeError("edge_tts is not installed")

        voice_map = {
            "en": "en-US-AriaNeural",
            "hi": "hi-IN-SwaraNeural",
            "ta": "ta-IN-PallaviNeural",
            "te": "te-IN-ShrutiNeural",
            "mr": "mr-IN-AarohiNeural",
        }

        base_lang = lang.split("-")[0].lower()
        voice = voice_map.get(base_lang, voice_map["en"])

        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        return audio_data

    def generate_speech(self, text: str, lang: str = "en") -> str:
        if not text:
            return ""

        if edge_tts is None:
            print("[EdgeTTS] edge_tts is not installed; skipping speech generation")
            return ""

        clean_text = text.replace("*", "").replace("#", "").strip()
        print(f"[EdgeTTS] Generating speech for: {clean_text[:30]}... ({lang})")

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            audio_data = loop.run_until_complete(self._generate_async(clean_text, lang))
            loop.close()

            if not audio_data:
                print("[EdgeTTS] Error: No audio data generated")
                return ""

            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
            return f"data:audio/mpeg;base64,{audio_base64}"

        except Exception as e:
            print(f"[EdgeTTS] Error: {e}")
            import traceback

            traceback.print_exc()
            return ""


_tts = EdgeTTSProvider()


def generate_speech(text: str, lang: str = "en") -> str:
    """Wrapper function used by the chat handler."""
    return _tts.generate_speech(text, lang)
