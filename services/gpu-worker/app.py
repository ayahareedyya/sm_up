"""
SM_UP GPU Worker Service
خدمة معالجة الصور باستخدام Flux Dev + LoRA
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from loguru import logger

from core.config import settings
from core.models import UpscaleRequest, UpscaleResponse, HealthResponse
from core.upscaler import FluxUpscaler
from core.monitoring import setup_monitoring
from utils.file_handler import FileHandler
from utils.gpu_monitor import GPUMonitor


# Global instances
upscaler = None
file_handler = None
gpu_monitor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """إدارة دورة حياة التطبيق"""
    global upscaler, file_handler, gpu_monitor
    
    logger.info("🚀 بدء تشغيل GPU Worker Service...")
    
    try:
        # Initialize components
        file_handler = FileHandler()
        gpu_monitor = GPUMonitor()
        upscaler = FluxUpscaler()
        
        # Load models
        await upscaler.load_models()
        
        logger.success("✅ تم تحميل جميع المكونات بنجاح")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ خطأ في تشغيل الخدمة: {e}")
        raise
    finally:
        logger.info("🔄 إيقاف GPU Worker Service...")
        if upscaler:
            await upscaler.cleanup()


# Create FastAPI app
app = FastAPI(
    title="SM_UP GPU Worker",
    description="خدمة معالجة الصور باستخدام Flux Dev + LoRA",
    version="1.0.0",
    lifespan=lifespan
)

# Setup monitoring
setup_monitoring(app)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """فحص صحة الخدمة"""
    try:
        gpu_info = gpu_monitor.get_gpu_status()
        memory_info = gpu_monitor.get_memory_usage()
        
        return HealthResponse(
            status="healthy",
            gpu_available=gpu_info["available"],
            gpu_memory_used=gpu_info["memory_used"],
            gpu_memory_total=gpu_info["memory_total"],
            system_memory_used=memory_info["used"],
            system_memory_total=memory_info["total"]
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.post("/upscale", response_model=UpscaleResponse)
async def upscale_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prompt: str = "high quality, detailed, sharp, professional photography"
):
    """رفع جودة الصورة"""
    
    if not upscaler:
        raise HTTPException(status_code=503, detail="Upscaler not initialized")
    
    # Validate file
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        logger.info(f"📥 استلام طلب معالجة صورة: {file.filename}")
        
        # Save uploaded file
        input_path = await file_handler.save_upload(file)
        
        # Validate image
        if not await file_handler.validate_image(input_path):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Process image
        result = await upscaler.upscale_image(input_path, prompt)
        
        # Schedule cleanup
        background_tasks.add_task(file_handler.cleanup_temp_files, [input_path])
        
        logger.success(f"✅ تم معالجة الصورة بنجاح: {result.output_path}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الصورة: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/status")
async def get_status():
    """حالة الخدمة التفصيلية"""
    try:
        return {
            "service": "gpu-worker",
            "status": "running",
            "models_loaded": upscaler.is_loaded if upscaler else False,
            "gpu_status": gpu_monitor.get_detailed_status(),
            "queue_size": 0,  # سيتم تطويره لاحقاً
            "processed_today": 0  # سيتم تطويره لاحقاً
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/metrics")
async def get_metrics():
    """مقاييس الأداء للمراقبة"""
    try:
        return {
            "gpu_utilization": gpu_monitor.get_gpu_utilization(),
            "memory_usage": gpu_monitor.get_memory_usage(),
            "temperature": gpu_monitor.get_gpu_temperature(),
            "processing_time_avg": 0,  # سيتم تطويره لاحقاً
            "success_rate": 100  # سيتم تطويره لاحقاً
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    logger.info("🔥 تشغيل GPU Worker Service...")
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
