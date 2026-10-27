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

## طبقة الأدوات (Tool Integration Layer)

يدعم النظام الآن استدعاء أدوات خارجية من قِبل النموذج اللغوي (Function Calling + ReAct).

### الأدوات الجاهزة للاختبار
- `get_current_time(timezone?: string)` – إرجاع الوقت والتاريخ الحاليين
- `book_appointment(patient_name: string, date: string, time: string, reason?: string)` – يحاكي حجز موعد ويخزنه في الذاكرة

### التحقق من الأدوات
بعد تشغيل السيرفر افتح: [http://localhost:8000/tools](http://localhost:8000/tools)

### كيفية إضافة أداة جديدة
1. أضف مخططها في `backend/tools/schemas.py` باستخدام `pydantic` (اختياري)
2. أضف دالة التنفيذ في `backend/tools/examples.py` أو ملف جديد
3. سجّلها عبر `registry.register(...)` واربطها بـ `tool_executor.register_pydantic(...)` إن لزم الأمر
4. سيُسجّل تلقائياً عند استيراد `backend.tools`

