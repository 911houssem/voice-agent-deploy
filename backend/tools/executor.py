# -*- coding: utf-8 -*-
"""
محرك تنفيذ الأدوات (Tool Execution Engine)
يتحقق من المعاملات، يدعم sync/async، ويُعيد نتيجة موحدة
"""

import asyncio
import json
from typing import Any, Dict

from pydantic import BaseModel, ValidationError

from .registry import ToolRegistry, Tool


class ToolExecutionResult:
    def __init__(self, success: bool, data: Any = None, error: str = None, tool: str = None):
        self.success = success
        self.data = data
        self.error = error
        self.tool = tool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "tool": self.tool,
            "data": self.data,
            "error": self.error,
        }

    def to_message_for_llm(self) -> str:
        """تحويل النتيجة لرسالة مفهومة يمكن إعادتها للنموذج"""
        if self.success:
            try:
                data_str = json.dumps(self.data, ensure_ascii=False, indent=2)
            except Exception:
                data_str = str(self.data)
            return f"[نتيجة أداة: {self.tool} - نجاح]\n{data_str}"
        else:
            return f"[نتيجة أداة: {self.tool} - فشل]\nسبب الخطأ: {self.error}\nيرجى الاعتذار للمستخدم بشكل مناسب أو اقتراح بديل إن أمكن."


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self._pydantic_map = {}

    def register_pydantic(self, tool_name: str, model_cls: type[BaseModel]):
        """ربط أداة بنموذج Pydantic للتحقق الصارم"""
        self._pydantic_map[tool_name] = model_cls

    async def execute(self, tool_name: str, args: Dict[str, Any] | None = None) -> ToolExecutionResult:
        args = args or {}
        tool: Tool | None = self.registry.get(tool_name)
        if not tool:
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                error=f"الأداة '{tool_name}' غير مسجلة في ToolRegistry.",
            )

        # التحقق من المعاملات
        if tool_name in self._pydantic_map:
            model_cls = self._pydantic_map[tool_name]
            try:
                validated = model_cls(**args)
                args_to_pass = validated.model_dump()
            except ValidationError as ve:
                errors = []
                for err in ve.errors():
                    loc = "->".join(str(x) for x in err.get("loc", []))
                    msg = err.get("msg", "خطأ في التحقق")
                    errors.append(f"- {loc}: {msg}")
                return ToolExecutionResult(
                    success=False,
                    tool=tool_name,
                    error="فشل التحقق من معاملات الأداة:\n" + "\n".join(errors),
                )
        else:
            args_to_pass = dict(args)

        # تنفيذ الأداة
        try:
            if tool.is_async:
                result = await tool.func(**args_to_pass)
            else:
                result = await asyncio.to_thread(tool.func, **args_to_pass)
            return ToolExecutionResult(success=True, tool=tool_name, data=result)
        except TypeError as te:
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                error=f"خطأ في تمرير المعاملات: {te}. تأكد من تطابق الأسماء مع المخطط.",
            )
        except TimeoutError:
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                error="انتهت مهلة تنفيذ الأداة. حاول مرة أخرى.",
            )
        except Exception as ex:
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                error=f"حدث استثناء أثناء تنفيذ الأداة: {ex}",
            )
