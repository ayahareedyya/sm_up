"""
مراقب GPU - مراقبة استخدام GPU والذاكرة
"""

import psutil
import torch
from typing import Dict, Optional
from loguru import logger

try:
    import GPUtil
    GPUTIL_AVAILABLE = True
except ImportError:
    GPUTIL_AVAILABLE = False
    logger.warning("GPUtil غير متوفر - سيتم استخدام PyTorch فقط لمراقبة GPU")


class GPUMonitor:
    """مراقب GPU والنظام"""
    
    def __init__(self):
        self.cuda_available = torch.cuda.is_available()
        self.device_count = torch.cuda.device_count() if self.cuda_available else 0
        
        if self.cuda_available:
            logger.info(f"🎮 تم العثور على {self.device_count} GPU")
            for i in range(self.device_count):
                gpu_name = torch.cuda.get_device_name(i)
                logger.info(f"  GPU {i}: {gpu_name}")
        else:
            logger.warning("⚠️ CUDA غير متوفر")
    
    def get_gpu_status(self) -> Dict:
        """حالة GPU الأساسية"""
        if not self.cuda_available:
            return {
                "available": False,
                "device_count": 0,
                "memory_used": 0.0,
                "memory_total": 0.0,
                "utilization": 0.0
            }
        
        try:
            # استخدام PyTorch للحصول على معلومات الذاكرة
            device = torch.cuda.current_device()
            memory_allocated = torch.cuda.memory_allocated(device)
            memory_reserved = torch.cuda.memory_reserved(device)
            memory_total = torch.cuda.get_device_properties(device).total_memory
            
            # تحويل إلى GB
            memory_used_gb = memory_reserved / (1024**3)
            memory_total_gb = memory_total / (1024**3)
            
            # محاولة الحصول على معلومات الاستخدام
            utilization = 0.0
            if GPUTIL_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus and len(gpus) > device:
                        utilization = gpus[device].load * 100
                except:
                    pass
            
            return {
                "available": True,
                "device_count": self.device_count,
                "current_device": device,
                "memory_used": round(memory_used_gb, 2),
                "memory_total": round(memory_total_gb, 2),
                "memory_allocated": round(memory_allocated / (1024**3), 2),
                "utilization": round(utilization, 1)
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على حالة GPU: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def get_detailed_status(self) -> Dict:
        """حالة GPU المفصلة"""
        basic_status = self.get_gpu_status()
        
        if not basic_status.get("available", False):
            return basic_status
        
        try:
            detailed = basic_status.copy()
            
            # معلومات إضافية من PyTorch
            device = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(device)
            
            detailed.update({
                "device_name": props.name,
                "compute_capability": f"{props.major}.{props.minor}",
                "multiprocessor_count": props.multi_processor_count,
                "total_memory_gb": round(props.total_memory / (1024**3), 2),
                "memory_usage_percent": round(
                    (basic_status["memory_used"] / basic_status["memory_total"]) * 100, 1
                )
            })
            
            # معلومات إضافية من GPUtil إذا كان متوفراً
            if GPUTIL_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus and len(gpus) > device:
                        gpu = gpus[device]
                        detailed.update({
                            "temperature": gpu.temperature,
                            "power_draw": getattr(gpu, 'powerDraw', None),
                            "power_limit": getattr(gpu, 'powerLimit', None),
                            "driver_version": getattr(gpu, 'driver', None)
                        })
                except Exception as e:
                    logger.debug(f"تعذر الحصول على معلومات GPUtil: {e}")
            
            return detailed
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الحالة المفصلة: {e}")
            return basic_status
    
    def get_memory_usage(self) -> Dict:
        """استخدام ذاكرة النظام"""
        try:
            memory = psutil.virtual_memory()
            
            return {
                "total": round(memory.total / (1024**3), 2),
                "used": round(memory.used / (1024**3), 2),
                "available": round(memory.available / (1024**3), 2),
                "percent": memory.percent
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على استخدام الذاكرة: {e}")
            return {"error": str(e)}
    
    def get_gpu_utilization(self) -> float:
        """نسبة استخدام GPU"""
        if not GPUTIL_AVAILABLE or not self.cuda_available:
            return 0.0
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                device = torch.cuda.current_device()
                if len(gpus) > device:
                    return round(gpus[device].load * 100, 1)
        except Exception as e:
            logger.debug(f"تعذر الحصول على استخدام GPU: {e}")
        
        return 0.0
    
    def get_gpu_temperature(self) -> Optional[float]:
        """درجة حرارة GPU"""
        if not GPUTIL_AVAILABLE or not self.cuda_available:
            return None
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                device = torch.cuda.current_device()
                if len(gpus) > device:
                    return gpus[device].temperature
        except Exception as e:
            logger.debug(f"تعذر الحصول على درجة حرارة GPU: {e}")
        
        return None
    
    def get_system_stats(self) -> Dict:
        """إحصائيات النظام الشاملة"""
        try:
            # معلومات CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # معلومات الذاكرة
            memory = self.get_memory_usage()
            
            # معلومات القرص
            disk = psutil.disk_usage('/')
            
            # معلومات GPU
            gpu_status = self.get_gpu_status()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": cpu_count
                },
                "memory": memory,
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 1)
                },
                "gpu": gpu_status
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على إحصائيات النظام: {e}")
            return {"error": str(e)}
    
    def check_gpu_health(self) -> Dict:
        """فحص صحة GPU"""
        health_status = {
            "healthy": True,
            "warnings": [],
            "errors": []
        }
        
        try:
            gpu_status = self.get_detailed_status()
            
            if not gpu_status.get("available", False):
                health_status["healthy"] = False
                health_status["errors"].append("GPU غير متوفر")
                return health_status
            
            # فحص استخدام الذاكرة
            memory_percent = gpu_status.get("memory_usage_percent", 0)
            if memory_percent > 90:
                health_status["warnings"].append(f"استخدام ذاكرة GPU عالي: {memory_percent}%")
            elif memory_percent > 95:
                health_status["healthy"] = False
                health_status["errors"].append(f"ذاكرة GPU ممتلئة تقريباً: {memory_percent}%")
            
            # فحص درجة الحرارة
            temperature = gpu_status.get("temperature")
            if temperature:
                if temperature > 80:
                    health_status["warnings"].append(f"درجة حرارة GPU عالية: {temperature}°C")
                elif temperature > 90:
                    health_status["healthy"] = False
                    health_status["errors"].append(f"درجة حرارة GPU خطيرة: {temperature}°C")
            
            return health_status
            
        except Exception as e:
            health_status["healthy"] = False
            health_status["errors"].append(f"خطأ في فحص صحة GPU: {e}")
            return health_status
