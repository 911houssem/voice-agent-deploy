# -*- coding: utf-8 -*-
"""
Modal deployment for voice-agent-deploy
يستضيف FastAPI + Voxtral + Silma TTS مع تحميل النماذج من Modal Volume
"""

import os
import sys
from pathlib import Path

import modal

app = modal.App("voice-agent-arabic")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install(
        "ffmpeg",
        "libsndfile1",
        "portaudio19-dev",
        "git",
        "curl",
        "wget",
        "build-essential",
    )
    .pip_install("pip", "wheel", "setuptools")
    .pip_install_from_requirements("requirements.txt")
    .copy_local_dir(".", remote_path="/app", ignore=[".git", "__pycache__", "*.pyc", ".venv", "venv", "models", "tmp", "assets/*.wav"])
)

models_volume = modal.Volume.from_name("voice-agent-models", create_if_missing=True)
tmp_volume = modal.Volume.from_name("voice-agent-tmp", create_if_missing=True)


@app.function(
    image=image,
    gpu="A10G",
    timeout=60 * 60 * 3,
    volumes={
        "/models": models_volume,
        "/app/tmp": tmp_volume,
    },
    scaledown_window=300,
    max_containers=1,
)
@modal.asgi_app()
def web():
    os.environ["VOXTRAL_MODEL_PATH"] = "/models/voxtral-ar"
    os.environ["SILMA_TTS_DIR"] = "/models/silma-tts"
    os.environ["REF_AUDIO_PATH"] = "/app/assets/assistant_ref.wav"
    os.environ["HOST"] = "0.0.0.0"
    os.environ["PORT"] = "8000"

    os.makedirs("/app/assets", exist_ok=True)
    os.makedirs("/app/tmp", exist_ok=True)
    os.makedirs("/models", exist_ok=True)

    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

    print("[MODAL] بدء تحميل التطبيق...")
    print(f"[MODAL] VOXTRAL_MODEL_PATH = {os.environ['VOXTRAL_MODEL_PATH']}")
    print(f"[MODAL] SILMA_TTS_DIR = {os.environ['SILMA_TTS_DIR']}")

    from backend.main import app as fastapi_app
    return fastapi_app
