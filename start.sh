#!/usr/bin/env bash
set -e

echo "[START] Checking models..."
if [ ! -d "/app/models/voxtral-ar" ] || [ ! -d "/app/models/silma-tts" ]; then
  echo "[WARN] models/ غير موجودة، سأحاول الربط..."
  python link_models.py || true
fi

echo "[START] Pulling Ollama model if needed..."
if command -v ollama >/dev/null 2>&1; then
  ollama serve > /dev/null 2>&1 &
  sleep 5
  ollama pull ${OLLAMA_MODEL:-qwen2.5:7b-instruct} || true
fi

echo "[START] Launching FastAPI on 0.0.0.0:8000"
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1
