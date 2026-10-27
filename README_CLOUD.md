# مساعد صوتي محلي مُجهّز للسحابة (Voxtral + Silma TTS + Ollama)

هذا المشروع مدمج بين:
- **Voxtral Mini 4B Realtime Arabic** للاستماع وتحويل الكلام لنص
- **Ollama + LLM** للفهم والإجابة
- **Silma TTS v1** لتحويل الإجابة لصوت

يعمل بالكامل محليًا أو على منصة سحابية مع GPU مثل RunPod / Vast.ai / Modal.

## 1) ربط النماذج
```bash
python link_models.py
```
سيقوم بربط مجلدي `silma tts` و`للاستماع (ASR) Voxtral Mini 4B Realtime Arabic` إلى `models/`.

## 2) تجهيز ملف الصوت المرجعي
ضع ملف `assistant_ref.wav` في مجلد `assets/` وحدّث `REF_TEXT` في ملف `.env`.

## 3) التشغيل محليًا باستخدام Docker
```bash
cp .env.example .env
docker-compose up --build
```
افتح: http://localhost:8000

## 4) التشغيل مع uvicorn مباشرةً
```bash
python -m venv .venv
source .venv/bin/activate  # ويندوز: .venv\Scripts\activate
pip install -r requirements.txt
ollama serve &
ollama pull qwen2.5:7b-instruct
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## متطلبات السحابة
- GPU مع 12GB+ (يفضل 16GB)
- RAM 16GB+
- CUDA 12.x
