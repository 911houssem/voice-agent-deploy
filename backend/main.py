# -*- coding: utf-8 -*-
import asyncio
import uuid
import wave
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from .config import settings, FRONTEND_DIR, TMP_DIR, ASSETS_DIR
from .vad import VAD
from .llm import LLM
from .loader import loader

# استيراد طبقة الأدوات لضمان تسجيلها
from . import tools  # noqa

app = FastAPI(title="Voice Agent - Cloud Ready", version="1.0.0")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

llm = LLM()


@app.on_event("startup")
async def startup_event():
    print("[STARTUP] Preloading models...")
    try:
        loader.load_stt()
    except Exception as e:
        print(f"[STARTUP][WARN] STT load failed: {e}")
    try:
        loader.load_tts()
    except Exception as e:
        print(f"[STARTUP][WARN] TTS load failed: {e}")
    try:
        from .tools import tool_registry
        print("[STARTUP] الأدوات المسجلة:")
        for name, tool in tool_registry.list_tools().items():
            print(f"  - {name}: {tool.description}")
    except Exception as e:
        print(f"[STARTUP][WARN] لم يتم عرض الأدوات: {e}")
    print("[STARTUP] Ready")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/tools")
async def list_tools():
    from .tools import tool_registry
    result = []
    for name, tool in tool_registry.list_tools().items():
        result.append(
            {
                "name": tool.name,
                "description": tool.description,
                "parameters_schema": tool.parameters_schema,
                "is_async": tool.is_async,
            }
        )
    return {"count": len(result), "tools": result}


@app.get("/health")
async def health():
    return {"status": "ok", "cuda": loader.device}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    vad = VAD(settings.VAD_AGGRESSIVENESS, settings.CHUNK_MS, settings.SAMPLE_RATE)
    audio_buffer = bytearray()
    recording = False
    silence_frames = 0
    max_silence = int(settings.SILENCE_TIMEOUT_MS / settings.CHUNK_MS)
    max_bytes = int(settings.MAX_UTTERANCE_SEC * settings.SAMPLE_RATE * 2)

    try:
        while True:
            data = await ws.receive_bytes()
            if not recording:
                if vad.is_speech(data):
                    recording = True
                    audio_buffer.clear()
                    audio_buffer.extend(data)
                    await ws.send_json({"type": "status", "msg": "أستمع..."})
            else:
                audio_buffer.extend(data)
                if vad.is_speech(data):
                    silence_frames = 0
                else:
                    silence_frames += 1
                if silence_frames >= max_silence or len(audio_buffer) >= max_bytes:
                    fname = TMP_DIR / f"{uuid.uuid4()}.wav"
                    with wave.open(str(fname), "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(settings.SAMPLE_RATE)
                        wf.writeframes(bytes(audio_buffer))
                    await ws.send_json({"type": "status", "msg": "أحوّل الكلام لنص..."})
                    try:
                        stt = loader.load_stt()
                        text = stt.transcribe_wav(str(fname))
                    except Exception as e:
                        text = ""
                        await ws.send_json({"type": "error", "msg": f"خطأ STT: {e}"})
                    if text.strip():
                        await ws.send_json({"type": "user", "text": text})
                        await ws.send_json({"type": "status", "msg": "أفكر..."})
                        answer = await llm.chat(text)
                        await ws.send_json({"type": "assistant", "text": answer})
                        await ws.send_json({"type": "status", "msg": "أُجيب صوتياً..."})
                        out_wav = TMP_DIR / f"{uuid.uuid4()}_reply.wav"
                        try:
                            ref_audio = Path(settings.REF_AUDIO_PATH)
                            if not ref_audio.exists():
                                await ws.send_json({"type": "error", "msg": "ضع assistant_ref.wav في assets/ مع REF_TEXT صحيح"})
                            else:
                                tts = loader.load_tts()
                                tts.synthesize(answer, str(ref_audio), settings.REF_TEXT or "", str(out_wav))
                                await ws.send_json({"type": "audio", "url": f"/audio/{out_wav.name}"})
                        except Exception as e:
                            await ws.send_json({"type": "error", "msg": f"خطأ TTS: {e}"})
                    recording = False
                    silence_frames = 0
                    audio_buffer.clear()
                    await ws.send_json({"type": "status", "msg": "جاهز"})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await ws.send_json({"type": "error", "msg": str(e)})


@app.get("/audio/{name}")
async def get_audio(name: str):
    path = TMP_DIR / name
    if not path.exists():
        return {"error": "not found"}
    return FileResponse(path, media_type="audio/wav")

