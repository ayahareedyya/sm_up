"""
نماذج البيانات لـ GPU Worker Service
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class ProcessingStatus(str, Enum):
    """حالات المعالجة"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageFormat(str, Enum):
    """صيغ الصور المدعومة"""
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"


class UpscaleRequest(BaseModel):
    """طلب رفع جودة الصورة"""
    
    prompt: str = Field(
        default="high quality, detailed, sharp, professional photography",
        description="وصف لتحسين الصورة",
        min_length=1,
        max_length=500
    )
    negative_prompt: Optional[str] = Field(
        default="blurry, low quality, pixelated",
        description="وصف سلبي لتجنبه",
        max_length=200
    )
    num_inference_steps: int = Field(
        default=20,
        description="عدد خطوات المعالجة",
        ge=10,
        le=50
    )
    guidance_scale: float = Field(
        default=7.5,
        description="قوة التوجيه",
        ge=1.0,
        le=20.0
    )
    strength: float = Field(
        default=0.8,
        description="قوة التعديل",
        ge=0.1,
        le=1.0
    )
    seed: Optional[int] = Field(
        default=None,
        description="البذرة للتكرار",
        ge=0
    )
    
    @validator('prompt')
    def validate_prompt(cls, v):
        if not v.strip():
            raise ValueError('Prompt cannot be empty')
        return v.strip()


class UpscaleResponse(BaseModel):
    """استجابة رفع جودة الصورة"""
    
    task_id: str = Field(description="معرف المهمة")
    status: ProcessingStatus = Field(description="حالة المعالجة")
    output_path: Optional[str] = Field(default=None, description="مسار الصورة المعالجة")
    download_url: Optional[str] = Field(default=None, description="رابط التحميل")
    processing_time: Optional[float] = Field(default=None, description="وقت المعالجة بالثواني")
    original_size: Optional[tuple] = Field(default=None, description="حجم الصورة الأصلية")
    output_size: Optional[tuple] = Field(default=None, description="حجم الصورة المعالجة")
    file_size: Optional[int] = Field(default=None, description="حجم الملف بالبايت")
    created_at: datetime = Field(default_factory=datetime.now, description="وقت الإنشاء")
    completed_at: Optional[datetime] = Field(default=None, description="وقت الانتهاء")
    error_message: Optional[str] = Field(default=None, description="رسالة الخطأ")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="معلومات إضافية")


class HealthResponse(BaseModel):
    """استجابة فحص الصحة"""
    
    status: str = Field(description="حالة الخدمة")
    timestamp: datetime = Field(default_factory=datetime.now, description="وقت الفحص")
    gpu_available: bool = Field(description="توفر GPU")
    gpu_memory_used: float = Field(description="ذاكرة GPU المستخدمة (GB)")
    gpu_memory_total: float = Field(description="إجمالي ذاكرة GPU (GB)")
    gpu_utilization: Optional[float] = Field(default=None, description="استخدام GPU (%)")
    system_memory_used: float = Field(description="ذاكرة النظام المستخدمة (GB)")
    system_memory_total: float = Field(description="إجمالي ذاكرة النظام (GB)")
    models_loaded: bool = Field(default=False, description="حالة تحميل الموديلات")
    queue_size: int = Field(default=0, description="حجم الطابور")


class ProcessingMetrics(BaseModel):
    """مقاييس الأداء"""
    
    total_processed: int = Field(default=0, description="إجمالي الصور المعالجة")
    successful_processed: int = Field(default=0, description="الصور المعالجة بنجاح")
    failed_processed: int = Field(default=0, description="الصور الفاشلة")
    average_processing_time: float = Field(default=0.0, description="متوسط وقت المعالجة")
    gpu_utilization_avg: float = Field(default=0.0, description="متوسط استخدام GPU")
    memory_usage_avg: float = Field(default=0.0, description="متوسط استخدام الذاكرة")
    uptime: float = Field(default=0.0, description="وقت التشغيل بالساعات")
    last_reset: datetime = Field(default_factory=datetime.now, description="آخر إعادة تعيين")


class ErrorResponse(BaseModel):
    """استجابة الخطأ"""
    
    error: str = Field(description="نوع الخطأ")
    message: str = Field(description="رسالة الخطأ")
    details: Optional[Dict[str, Any]] = Field(default=None, description="تفاصيل إضافية")
    timestamp: datetime = Field(default_factory=datetime.now, description="وقت الخطأ")
    request_id: Optional[str] = Field(default=None, description="معرف الطلب")


class ModelInfo(BaseModel):
    """معلومات الموديل"""
    
    name: str = Field(description="اسم الموديل")
    version: str = Field(description="إصدار الموديل")
    size: Optional[str] = Field(default=None, description="حجم الموديل")
    loaded: bool = Field(description="حالة التحميل")
    load_time: Optional[float] = Field(default=None, description="وقت التحميل")
    memory_usage: Optional[float] = Field(default=None, description="استخدام الذاكرة")


class ServiceStatus(BaseModel):
    """حالة الخدمة الشاملة"""
    
    service_name: str = Field(default="gpu-worker", description="اسم الخدمة")
    version: str = Field(default="1.0.0", description="إصدار الخدمة")
    status: str = Field(description="حالة الخدمة")
    uptime: float = Field(description="وقت التشغيل")
    models: list[ModelInfo] = Field(default=[], description="معلومات الموديلات")
    metrics: ProcessingMetrics = Field(description="مقاييس الأداء")
    health: HealthResponse = Field(description="فحص الصحة")
    last_updated: datetime = Field(default_factory=datetime.now, description="آخر تحديث")
