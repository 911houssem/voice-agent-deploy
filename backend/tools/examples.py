# -*- coding: utf-8 -*-
"""
أدوات جاهزة للاختبار
1. get_current_time
2. book_appointment
"""

from datetime import datetime
from typing import Dict, Any

from .registry import ToolRegistry
from .schemas import GetCurrentTimeArgs, BookAppointmentArgs

# ذاكرة بسيطة لحجز المواعيد
_APPOINTMENTS: list[Dict[str, Any]] = []


def get_current_time(timezone: str | None = None) -> Dict[str, Any]:
    """إرجاع الوقت والتاريخ الحاليين"""
    try:
        try:
            import pytz
            if timezone:
                tz = pytz.timezone(timezone)
                now = datetime.now(tz)
            else:
                now = datetime.now()
        except Exception:
            now = datetime.now()
        return {
            "datetime_iso": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
            "timezone": timezone or "local",
        }
    except Exception as e:
        now = datetime.now()
        return {
            "datetime_iso": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "weekday": now.strftime("%A"),
            "timezone": "local",
            "note": f"تعذر استخدام المنطقة الزمنية المحددة، تم استخدام التوقيت المحلي. ({e})",
        }


def book_appointment(patient_name: str, date: str, time: str, reason: str | None = None) -> Dict[str, Any]:
    """محاكاة حجز موعد وتخزينه في الذاكرة"""
    appt_id = f"APT-{len(_APPOINTMENTS) + 1:04d}"
    appointment = {
        "appointment_id": appt_id,
        "patient_name": patient_name,
        "date": date,
        "time": time,
        "reason": reason or "غير محدد",
        "status": "مؤكد",
        "created_at": datetime.now().isoformat(),
    }
    _APPOINTMENTS.append(appointment)
    return {
        "message": "تم حجز الموعد بنجاح",
        "appointment": appointment,
        "total_appointments": len(_APPOINTMENTS),
    }


def register_examples(registry: ToolRegistry):
    """تسجيل الأدوات التجريبية وربطها بـ Pydantic للتحقق"""
    registry.register(
        name="get_current_time",
        description="الحصول على التاريخ والوقت الحاليين. يمكن تمرير timezone اختيارياً.",
        parameters_schema={
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "اسم المنطقة الزمنية مثل Asia/Riyadh",
                }
            },
            "required": [],
        },
        func=get_current_time,
    )
    from . import executor as _exec
    _exec.tool_executor.register_pydantic("get_current_time", GetCurrentTimeArgs)

    registry.register(
        name="book_appointment",
        description="حجز موعد للمريض وحفظه في الذاكرة لأغراض الاختبار.",
        parameters_schema={
            "type": "object",
            "properties": {
                "patient_name": {"type": "string", "description": "اسم المريض الكامل"},
                "date": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "pattern": r"^([01]\d|2[0-3]):([0-5]\d)$", "description": "HH:MM"},
                "reason": {"type": "string", "description": "سبب الحجز (اختياري)"},
            },
            "required": ["patient_name", "date", "time"],
        },
        func=book_appointment,
    )
    _exec.tool_executor.register_pydantic("book_appointment", BookAppointmentArgs)
