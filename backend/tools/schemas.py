# -*- coding: utf-8 -*-
"""
مخططات الأدوات باستخدام Pydantic
يُستخدم للتحقق من معاملات الأدوات قبل التنفيذ
"""

from pydantic import BaseModel, Field
from typing import Optional


class GetCurrentTimeArgs(BaseModel):
    """معاملات أداة get_current_time"""
    timezone: Optional[str] = Field(
        default=None,
        description="اسم المنطقة الزمنية مثل Asia/Riyadh أو Africa/Casablanca (اختياري)"
    )


class BookAppointmentArgs(BaseModel):
    """معاملات أداة book_appointment"""
    patient_name: str = Field(
        ..., 
        min_length=2, 
        max_length=80, 
        description="اسم المريض الكامل بالعربية أو الإنجليزية"
    )
    date: str = Field(
        ..., 
        pattern=r"^\d{4}-\d{2}-\d{2}$", 
        description="التاريخ بصيغة YYYY-MM-DD"
    )
    time: str = Field(
        ..., 
        pattern=r"^([01]\d|2[0-3]):([0-5]\d)$", 
        description="الوقت بصيغة HH:MM بصيغة 24 ساعة"
    )
    reason: Optional[str] = Field(
        default=None,
        max_length=200,
        description="سبب الحجز (اختياري)"
    )
