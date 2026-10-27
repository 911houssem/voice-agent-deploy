import os
import sys
from pathlib import Path
import torch

from .config import settings

class ModelLoader:
    def __init__(self):
        self.stt = None
        self.tts = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[LOADER] Device: {self.device}")

    def load_stt(self):
        if self.stt is not None:
            return self.stt
        from .stt_voxtral import VoxtralSTT
        print(f"[LOADER] Loading Voxtral from {settings.VOXTRAL_MODEL_PATH}")
        self.stt = VoxtralSTT(settings.VOXTRAL_MODEL_PATH)
        print("[LOADER] Voxtral loaded")
        return self.stt

    def load_tts(self):
        if self.tts is not None:
            return self.tts
        from .tts_silma import SilmaTTS
        print(f"[LOADER] Loading SilmaTTS from {settings.SILMA_TTS_DIR}")
        self.tts = SilmaTTS(settings.SILMA_TTS_DIR)
        print("[LOADER] SilmaTTS loaded")
        return self.tts

loader = ModelLoader()
