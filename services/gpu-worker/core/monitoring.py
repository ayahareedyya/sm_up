"""
نظام المراقبة والمقاييس
"""

import time
from typing import Dict
from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from loguru import logger


# Prometheus metrics
REQUEST_COUNT = Counter(
    'gpu_worker_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'gpu_worker_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

PROCESSING_TIME = Histogram(
    'gpu_worker_processing_time_seconds',
    'Image processing time in seconds'
)

ACTIVE_REQUESTS = Gauge(
    'gpu_worker_active_requests',
    'Number of active requests'
)

GPU_MEMORY_USAGE = Gauge(
    'gpu_worker_gpu_memory_usage_bytes',
    'GPU memory usage in bytes'
)

GPU_UTILIZATION = Gauge(
    'gpu_worker_gpu_utilization_percent',
    'GPU utilization percentage'
)

IMAGES_PROCESSED = Counter(
    'gpu_worker_images_processed_total',
    'Total number of images processed',
    ['status']
)


class MetricsCollector:
    """جامع المقاييس"""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.processing_times = []
        
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """تسجيل طلب"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        self.request_count += 1
    
    def record_processing_time(self, duration: float):
        """تسجيل وقت المعالجة"""
        PROCESSING_TIME.observe(duration)
        self.processing_times.append(duration)
        
        # الاحتفاظ بآخر 100 قياس فقط
        if len(self.processing_times) > 100:
            self.processing_times = self.processing_times[-100:]
    
    def record_image_processed(self, success: bool):
        """تسجيل معالجة صورة"""
        status = "success" if success else "failed"
        IMAGES_PROCESSED.labels(status=status).inc()
    
    def update_gpu_metrics(self, memory_usage: float, utilization: float):
        """تحديث مقاييس GPU"""
        GPU_MEMORY_USAGE.set(memory_usage)
        GPU_UTILIZATION.set(utilization)
    
    def get_summary(self) -> Dict:
        """ملخص المقاييس"""
        uptime = time.time() - self.start_time
        avg_processing_time = (
            sum(self.processing_times) / len(self.processing_times)
            if self.processing_times else 0
        )
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "average_processing_time": avg_processing_time,
            "recent_processing_times": self.processing_times[-10:] if self.processing_times else []
        }


# Global metrics collector
metrics_collector = MetricsCollector()


async def metrics_middleware(request: Request, call_next):
    """Middleware لتسجيل المقاييس"""
    start_time = time.time()
    
    # زيادة عداد الطلبات النشطة
    ACTIVE_REQUESTS.inc()
    
    try:
        response = await call_next(request)
        
        # حساب مدة الطلب
        duration = time.time() - start_time
        
        # تسجيل المقاييس
        metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
            duration=duration
        )
        
        return response
        
    except Exception as e:
        # تسجيل الأخطاء
        duration = time.time() - start_time
        metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status=500,
            duration=duration
        )
        raise
    
    finally:
        # تقليل عداد الطلبات النشطة
        ACTIVE_REQUESTS.dec()


def setup_monitoring(app: FastAPI):
    """إعداد نظام المراقبة"""
    
    # إضافة middleware
    app.middleware("http")(metrics_middleware)
    
    @app.get("/metrics")
    async def get_prometheus_metrics():
        """Prometheus metrics endpoint"""
        return Response(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    @app.get("/metrics/summary")
    async def get_metrics_summary():
        """ملخص المقاييس"""
        return metrics_collector.get_summary()
    
    logger.info("📊 تم إعداد نظام المراقبة")


def record_processing_time(duration: float):
    """تسجيل وقت المعالجة (للاستخدام الخارجي)"""
    metrics_collector.record_processing_time(duration)


def record_image_processed(success: bool):
    """تسجيل معالجة صورة (للاستخدام الخارجي)"""
    metrics_collector.record_image_processed(success)


def update_gpu_metrics(memory_usage: float, utilization: float):
    """تحديث مقاييس GPU (للاستخدام الخارجي)"""
    metrics_collector.update_gpu_metrics(memory_usage, utilization)
