# -*- coding: utf-8 -*-
"""
طبقة ربط الأدوات (Tool Integration Layer)
تهيئة سجل الأدوات وتحميل الأدوات التجريبية عند الاستيراد
"""

from .registry import ToolRegistry, Tool
from .executor import ToolExecutor
from . import examples  # تحميل الأدوات الجاهزة للاختبار

# إنشاء نسخة عامة قابلة للإستخدام
tool_registry = ToolRegistry()
tool_executor = ToolExecutor(tool_registry)

# تسجيل الأدوات التجريبية تلقائياً
examples.register_examples(tool_registry)

__all__ = [
    "Tool",
    "ToolRegistry",
    "ToolExecutor",
    "tool_registry",
    "tool_executor",
]
