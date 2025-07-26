"""
Flux Upscaler - معالج رفع جودة الصور
"""

import os
import time
import uuid
import asyncio
from typing import Optional, Tuple
from pathlib import Path
import torch
from PIL import Image
from loguru import logger
from diffusers import FluxPipeline
from diffusers.utils import load_image

from .config import settings, get_model_config, get_processing_config
from .models import UpscaleResponse, ProcessingStatus


class FluxUpscaler:
    """معالج رفع جودة الصور باستخدام Flux Dev + LoRA"""
    
    def __init__(self):
        self.pipeline = None
        self.is_loaded = False
        self.device = f"cuda:{settings.CUDA_DEVICE}"
        self.model_config = get_model_config()
        self.processing_config = get_processing_config()
        
        # إحصائيات
        self.total_processed = 0
        self.successful_processed = 0
        self.failed_processed = 0
        self.total_processing_time = 0.0
        
        logger.info(f"🔧 تم إنشاء FluxUpscaler للجهاز: {self.device}")
    
    async def load_models(self) -> bool:
        """تحميل الموديلات"""
        try:
            logger.info("📥 بدء تحميل موديلات Flux...")
            
            # التحقق من توفر GPU
            if not torch.cuda.is_available():
                raise RuntimeError("CUDA غير متوفر")
            
            # تحميل Flux pipeline
            logger.info(f"تحميل {self.model_config['flux_model']}...")
            
            self.pipeline = FluxPipeline.from_pretrained(
                self.model_config['flux_model'],
                torch_dtype=torch.bfloat16,
                device_map="auto"
            )
            
            # تحميل LoRA إذا كان متوفراً
            lora_path = self.model_config['lora_path']
            if os.path.exists(lora_path):
                logger.info(f"تحميل LoRA من: {lora_path}")
                self.pipeline.load_lora_weights(lora_path)
            else:
                logger.warning(f"LoRA غير موجود في: {lora_path}")
            
            # تحسين الذاكرة
            if self.model_config['enable_memory_efficient']:
                self.pipeline.enable_model_cpu_offload()
                self.pipeline.enable_attention_slicing()
            
            self.is_loaded = True
            logger.success("✅ تم تحميل جميع الموديلات بنجاح")
            return True
            
        except Exception as e:
            logger.error(f"❌ فشل في تحميل الموديلات: {e}")
            self.is_loaded = False
            return False
    
    async def upscale_image(
        self, 
        input_path: str, 
        prompt: str,
        **kwargs
    ) -> UpscaleResponse:
        """رفع جودة الصورة"""
        
        if not self.is_loaded:
            raise RuntimeError("الموديلات غير محملة")
        
        task_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            logger.info(f"🎨 بدء معالجة الصورة: {task_id}")
            
            # تحميل الصورة
            input_image = load_image(input_path)
            original_size = input_image.size
            
            # التحقق من حجم الصورة
            max_size = settings.MAX_IMAGE_SIZE
            if max(original_size) > max_size:
                # تصغير الصورة إذا كانت كبيرة جداً
                ratio = max_size / max(original_size)
                new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
                input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"تم تصغير الصورة من {original_size} إلى {new_size}")
            
            # إعداد المعاملات
            generation_params = {
                "prompt": prompt,
                "image": input_image,
                "num_inference_steps": kwargs.get("num_inference_steps", self.processing_config["num_inference_steps"]),
                "guidance_scale": kwargs.get("guidance_scale", self.processing_config["guidance_scale"]),
                "strength": kwargs.get("strength", self.processing_config["strength"]),
                "generator": torch.Generator(device=self.device).manual_seed(kwargs.get("seed", 42))
            }
            
            # إضافة negative prompt إذا كان متوفراً
            negative_prompt = kwargs.get("negative_prompt", self.processing_config["negative_prompt"])
            if negative_prompt:
                generation_params["negative_prompt"] = negative_prompt
            
            # معالجة الصورة
            logger.info("🔄 بدء عملية المعالجة...")
            
            with torch.inference_mode():
                result_image = self.pipeline(**generation_params).images[0]
            
            # حفظ النتيجة
            output_path = await self._save_result(result_image, task_id)
            
            # حساب الوقت
            processing_time = time.time() - start_time
            
            # تحديث الإحصائيات
            self.total_processed += 1
            self.successful_processed += 1
            self.total_processing_time += processing_time
            
            logger.success(f"✅ تم معالجة الصورة بنجاح في {processing_time:.2f} ثانية")
            
            return UpscaleResponse(
                task_id=task_id,
                status=ProcessingStatus.COMPLETED,
                output_path=output_path,
                processing_time=processing_time,
                original_size=original_size,
                output_size=result_image.size,
                file_size=os.path.getsize(output_path) if os.path.exists(output_path) else None
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            self.total_processed += 1
            self.failed_processed += 1
            
            logger.error(f"❌ فشل في معالجة الصورة {task_id}: {e}")
            
            return UpscaleResponse(
                task_id=task_id,
                status=ProcessingStatus.FAILED,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _save_result(self, image: Image.Image, task_id: str) -> str:
        """حفظ الصورة المعالجة"""
        try:
            # إنشاء مجلد النتائج إذا لم يكن موجوداً
            result_dir = Path(settings.RESULT_DIR)
            result_dir.mkdir(parents=True, exist_ok=True)
            
            # تحديد مسار الحفظ
            output_filename = f"upscaled_{task_id}.png"
            output_path = result_dir / output_filename
            
            # حفظ الصورة
            image.save(output_path, "PNG", optimize=True)
            
            logger.info(f"💾 تم حفظ النتيجة في: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ فشل في حفظ النتيجة: {e}")
            raise
    
    async def cleanup(self):
        """تنظيف الموارد"""
        try:
            if self.pipeline:
                del self.pipeline
                torch.cuda.empty_cache()
                logger.info("🧹 تم تنظيف موارد GPU")
        except Exception as e:
            logger.error(f"خطأ في التنظيف: {e}")
    
    def get_stats(self) -> dict:
        """إحصائيات المعالجة"""
        avg_time = (self.total_processing_time / self.total_processed 
                   if self.total_processed > 0 else 0)
        
        success_rate = (self.successful_processed / self.total_processed * 100 
                       if self.total_processed > 0 else 0)
        
        return {
            "total_processed": self.total_processed,
            "successful_processed": self.successful_processed,
            "failed_processed": self.failed_processed,
            "average_processing_time": avg_time,
            "success_rate": success_rate,
            "total_processing_time": self.total_processing_time
        }
