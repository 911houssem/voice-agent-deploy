# استضافة المشروع على Modal مع رفع النماذج

هذا الدليل يشرح كيفية رفع كود المشروع + ملفات النماذج كاملة على [Modal](https://modal.com/) وتشغيل المساعد الصوتي مباشرةً.

## 1) تجهيز المتطلبات

- حساب على [modal.com](https://modal.com/)
- تثبيت [Modal CLI](https://modal.com/docs/guide/cli)
- مجلدي النماذج محليًا: `models/voxtral-ar/` و `models/silma-tts/`
- ملف الصوت المرجعي `assets/assistant_ref.wav` (اختياري)

## 2) تسجيل الدخول لـ Modal

```bash
pip install modal
modal setup
```

## 3) رفع ملفات النماذج إلى Modal Volume

```bash
modal volume create voice-agent-models
modal volume put voice-agent-models ./models/voxtral-ar /voxtral-ar
modal volume put voice-agent-models ./models/silma-tts /silma-tts
modal volume ls voice-agent-models
```

## 4) نشر المشروع

```bash
modal deploy modal_app.py
```

بعد النشر سيظهر الرابط: `https://<your-username>--voice-agent-arabic-web-dev.modal.run`

## 5) تحديث المشروع

```bash
modal deploy modal_app.py
```

النماذج تبقى داخل Volume ولا تحتاج لإعادة رفعها.
