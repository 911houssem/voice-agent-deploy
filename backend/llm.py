import httpx
from .config import settings

class LLM:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.history = []

    async def chat(self, user_text: str):
        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}] + self.history[-12:]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                if resp.status_code == 404:
                    resp = await client.post(f"{self.base_url}/api/chat", json={"model": self.model, "messages": messages, "stream": False})
                resp.raise_for_status()
                data = resp.json()
                if "choices" in data:
                    answer = data["choices"][0]["message"]["content"].strip()
                elif "message" in data:
                    answer = data["message"]["content"].strip()
                else:
                    answer = str(data)
                self.history.append({"role": "assistant", "content": answer})
                return answer
            except Exception as e:
                return f"عذراً، حدث خطأ في الاتصال بنموذج الذكاء الاصطناعي: {e}"

    def reset(self):
        self.history = []
