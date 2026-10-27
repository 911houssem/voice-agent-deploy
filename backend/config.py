import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b-instruct"
    OLLAMA_TIMEOUT: int = 180

    VOXTRAL_MODEL_PATH: str = "/app/models/voxtral-ar"
    SILMA_TTS_DIR: str = "/app/models/silma-tts"

    SAMPLE_RATE: int = 16000
    CHUNK_MS: int = 30
    VAD_AGGRESSIVENESS: int = 2
    SILENCE_TIMEOUT_MS: int = 950
    MAX_UTTERANCE_SEC: int = 25

    SYSTEM_PROMPT: str = "أنت مساعد صوتي عربي ذكي، تتحدث بشكل طبيعي وواضح، موجزًا عند الحاجة ومفصلاً عند الطلب. تجيب مباشرة وبأسلوب ودود."
    REF_AUDIO_PATH: str = "/app/assets/assistant_ref.wav"
    REF_TEXT: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

APP_ROOT = Path("/app")
ROOT = Path(__file__).parent.parent
FRONTEND_DIR = ROOT / "frontend"
ASSETS_DIR = ROOT / "assets"
TMP_DIR = ROOT / "tmp"

for p in [ASSETS_DIR, TMP_DIR]:
    p.mkdir(exist_ok=True)
