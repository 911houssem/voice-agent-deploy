# -*- coding: utf-8 -*-
"""
سجل الأدوات (Tool Registry)
يدعم التسجيل الديناميكي للأدوات مع اسمها، وصفها، مخططها، ودالة التنفيذ
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional


@dataclass
class Tool:
    name: str
    description: str
    parameters_schema: Dict[str, Any]
    func: Callable
    is_async: bool = field(init=False)

    def __post_init__(self):
        # تحديد ما إذا كانت الدالة async
        self.is_async = inspect.iscoroutinefunction(self.func)


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters_schema: Dict[str, Any],
        func: Callable,
    ) -> None:
        """تسجيل أداة جديدة في السجل"""
        if name in self._tools:
            print(f"[ToolRegistry] تحذير: أداة '{name}' مسجلة مسبقًا، سيتم استبدالها.")
        self._tools[name] = Tool(
            name=name,
            description=description,
            parameters_schema=parameters_schema,
            func=func,
        )
        print(f"[ToolRegistry] تم تسجيل الأداة: {name}")

    def get(self, name: str) -> Optional[Tool]:
        """إرجاع أداة حسب الاسم"""
        return self._tools.get(name)

    def exists(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> Dict[str, Tool]:
        """إرجاع جميع الأدوات المسجلة"""
        return self._tools.copy()

    def get_tools_for_llm(self) -> list[Dict[str, Any]]:
        """
        إرجاع قائمة الأدوات بصيغة مناسبة لتمريرها لـ Ollama / LLM
        (متوافقة مع نمط Function/Tool Calling)
        """
        tools_list = []
        for tool in self._tools.values():
            tools_list.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters_schema,
                    },
                }
            )
        return tools_list

    def get_tools_prompt(self) -> str:
        """
        بديل في حال عدم دعم النموذج لـ Function Calling
        يُستخدم مع نمط ReAct لتمكين النموذج من request أداة بصيغة JSON صريحة
        """
        lines = []
        lines.append("أنت وكيل صوتي عربي ذكي لديك القدرة على استدعاء أدوات عند الحاجة فقط.")
        lines.append("عند الحاجة لاستخدام أداة، يجب أن تجيب بصيغة JSON EXACTLY كالتالي:")
        lines.append('{"tool": "اسم_الأداة", "args": { ... } }')
        lines.append("بعد الحصول على نتيجة الأداة، استخدمها للإجابة للمستخدم بشكل طبيعي وواضح بالعربية.")
        lines.append("\nالأدوات المتاحة:")
        for tool in self._tools.values():
            lines.append(f"- {tool.name}: {tool.description}")
            lines.append(f"  مخطط المعاملات: {tool.parameters_schema}")
        lines.append("\nإذا لم تكن بحاجة لأداة، أجب مباشرةً للمستخدم دون JSON.")
        return "\n".join(lines)
