# -*- coding: utf-8 -*-
"""
وحدة LLM مع دعم استدعاء الأدوات (Tool Calling)
يدعم Ollama /v1/chat/completions مع tools، واكتشاف طلب أداة بصيغة JSON، وحلقة تنفيذ متعددة
"""

import json
import re
from typing import Any, Dict, List

import httpx

from .config import settings
from .tools import tool_registry, tool_executor


class LLM:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        self.history: List[Dict[str, str]] = []
        self.max_tool_turns = 5
        self.enable_tools = True

    def _build_system_prompt(self) -> str:
        base = settings.SYSTEM_PROMPT
        if not self.enable_tools:
            return base
        tools_prompt = tool_registry.get_tools_prompt()
        return f"{base}\n\n{tools_prompt}"

    def _extract_tool_call(self, content: str) -> Dict[str, Any] | None:
        content = content.strip()
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        if isinstance(data, dict) and "tool" in data and isinstance(data.get("tool"), str):
            args = data.get("args") or {}
            if not isinstance(args, dict):
                args = {}
            return {"tool": data["tool"], "args": args}
        return None

    async def chat(self, user_text: str) -> str:
        if not user_text.strip():
            return "يرجى التحدث أو كتابة رسالة."

        self.history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": self._build_system_prompt()}] + self.history[-14:]
        tools_schema = tool_registry.get_tools_for_llm() if self.enable_tools else []

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            turn = 0
            while turn < self.max_tool_turns:
                turn += 1
                payload: Dict[str, Any] = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "stream": False,
                }
                if tools_schema:
                    payload["tools"] = tools_schema
                    payload["tool_choice"] = "auto"

                try:
                    resp = await client.post(f"{self.base_url}/v1/chat/completions", json=payload)
                    if resp.status_code == 404:
                        payload_fallback = {
                            "model": self.model,
                            "messages": messages,
                            "stream": False,
                            "options": {"temperature": 0.7, "top_p": 0.9},
                        }
                        resp = await client.post(f"{self.base_url}/api/chat", json=payload_fallback)
                    resp.raise_for_status()
                    data = resp.json()
                except Exception as e:
                    return f"عذراً، حدث خطأ في الاتصال بنموذج الذكاء الاصطناعي: {e}"

                assistant_content = ""
                tool_calls_from_api = []

                if "choices" in data and data["choices"]:
                    choice = data["choices"][0]
                    msg = choice.get("message") or {}
                    assistant_content = msg.get("content") or ""
                    if msg.get("tool_calls"):
                        tool_calls_from_api = msg.get("tool_calls") or []
                elif "message" in data:
                    msg = data["message"] or {}
                    assistant_content = msg.get("content") or ""
                    if msg.get("tool_calls"):
                        tool_calls_from_api = msg.get("tool_calls") or []

                assistant_content = (assistant_content or "").strip()

                if tool_calls_from_api:
                    for tc in tool_calls_from_api:
                        func = tc.get("function") or {}
                        tname = func.get("name")
                        targs_raw = func.get("arguments") or "{}"
                        try:
                            if isinstance(targs_raw, str):
                                targs = json.loads(targs_raw)
                            else:
                                targs = targs_raw
                        except json.JSONDecodeError:
                            targs = {}
                        res = await tool_executor.execute(tname, targs)
                        messages.append({"role": "tool", "content": res.to_message_for_llm()})
                    continue

                tool_call = self._extract_tool_call(assistant_content)
                if tool_call and self.enable_tools:
                    tname = tool_call["tool"]
                    targs = tool_call["args"]
                    messages.append({"role": "assistant", "content": assistant_content})
                    res = await tool_executor.execute(tname, targs)
                    messages.append(
                        {
                            "role": "user",
                            "content": res.to_message_for_llm() + "\n\nالآن أجب على المستخدم بالرد النهائي بالعربية بناءً على هذه النتيجة.",
                        }
                    )
                    continue

                if not assistant_content:
                    assistant_content = "عذراً، لم أتمكن من توليد رد الآن."
                self.history.append({"role": "assistant", "content": assistant_content})
                return assistant_content

            fallback = "تم إجراء عدة خطوات باستخدام الأدوات، لكن وصلت لحد أقصى من التكرار. إليك ملخص بناءً على آخر النتائج المتاحة."
            self.history.append({"role": "assistant", "content": fallback})
            return fallback

    def reset(self):
        self.history = []

