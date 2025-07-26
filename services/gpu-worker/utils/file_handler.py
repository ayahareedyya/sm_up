"""
معالج الملفات - إدارة رفع وحفظ ومعالجة الملفات
"""

import os
import uuid
import aiofiles
from pathlib import Path
from typing import List, Optional
from PIL import Image
from fastapi import UploadFile
from loguru import logger

from core.config import settings, get_file_config


class FileHandler:
    """معالج الملفات"""
    
    def __init__(self):
        self.config = get_file_config()
        self._ensure_directories()
        logger.info("📁 تم تهيئة معالج الملفات")
    
    def _ensure_directories(self):
        """إنشاء المجلدات المطلوبة"""
        directories = [
            self.config["upload_dir"],
            self.config["result_dir"],
            self.config["temp_dir"]
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            logger.debug(f"📂 تم التأكد من وجود المجلد: {directory}")
    
    async def save_upload(self, file: UploadFile) -> str:
        """حفظ الملف المرفوع"""
        try:
            # التحقق من حجم الملف
            if file.size and file.size > self.config["max_file_size"]:
                raise ValueError(f"حجم الملف كبير جداً: {file.size} bytes")
            
            # إنشاء اسم ملف فريد
            file_extension = self._get_file_extension(file.filename)
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = Path(self.config["upload_dir"]) / unique_filename
            
            # حفظ الملف
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"📥 تم حفظ الملف: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"❌ فشل في حفظ الملف: {e}")
            raise
    
    async def validate_image(self, file_path: str) -> bool:
        """التحقق من صحة الصورة"""
        try:
            with Image.open(file_path) as img:
                # التحقق من صيغة الصورة
                if img.format not in self.config["supported_formats"]:
                    logger.warning(f"صيغة غير مدعومة: {img.format}")
                    return False
                
                # التحقق من حجم الصورة
                width, height = img.size
                max_size = self.config["max_image_size"]
                
                if width > max_size or height > max_size:
                    logger.warning(f"حجم الصورة كبير: {width}x{height}")
                    # لا نرفض الصورة، بل سنقوم بتصغيرها في المعالج
                
                # التحقق من أن الصورة ليست فارغة
                if width < 10 or height < 10:
                    logger.warning(f"حجم الصورة صغير جداً: {width}x{height}")
                    return False
                
                logger.info(f"✅ صورة صحيحة: {width}x{height}, {img.format}")
                return True
                
        except Exception as e:
            logger.error(f"❌ خطأ في التحقق من الصورة: {e}")
            return False
    
    async def cleanup_temp_files(self, file_paths: List[str]):
        """تنظيف الملفات المؤقتة"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"🗑️ تم حذف الملف المؤقت: {file_path}")
            except Exception as e:
                logger.warning(f"تعذر حذف الملف {file_path}: {e}")
    
    async def cleanup_old_files(self, max_age_hours: int = 24):
        """تنظيف الملفات القديمة"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        directories = [
            self.config["upload_dir"],
            self.config["temp_dir"]
        ]
        
        cleaned_count = 0
        
        for directory in directories:
            try:
                for file_path in Path(directory).iterdir():
                    if file_path.is_file():
                        file_age = current_time - file_path.stat().st_mtime
                        if file_age > max_age_seconds:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"🗑️ تم حذف ملف قديم: {file_path}")
            except Exception as e:
                logger.warning(f"خطأ في تنظيف المجلد {directory}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"🧹 تم تنظيف {cleaned_count} ملف قديم")
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """الحصول على معلومات الملف"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            # معلومات أساسية
            info = {
                "path": file_path,
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime
            }
            
            # معلومات الصورة إذا كانت صورة
            try:
                with Image.open(file_path) as img:
                    info.update({
                        "format": img.format,
                        "mode": img.mode,
                        "size": img.size,
                        "width": img.width,
                        "height": img.height
                    })
            except:
                pass  # ليس ملف صورة
            
            return info
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات الملف: {e}")
            return None
    
    def _get_file_extension(self, filename: Optional[str]) -> str:
        """استخراج امتداد الملف"""
        if not filename:
            return ".jpg"
        
        extension = Path(filename).suffix.lower()
        
        # تحويل الامتدادات الشائعة
        extension_map = {
            ".jpeg": ".jpg",
            ".png": ".png",
            ".webp": ".webp"
        }
        
        return extension_map.get(extension, ".jpg")
    
    async def create_download_url(self, file_path: str, base_url: str = "") -> str:
        """إنشاء رابط تحميل"""
        try:
            filename = Path(file_path).name
            return f"{base_url}/download/{filename}"
        except Exception as e:
            logger.error(f"خطأ في إنشاء رابط التحميل: {e}")
            return ""
    
    def get_storage_stats(self) -> dict:
        """إحصائيات التخزين"""
        try:
            stats = {}
            
            directories = {
                "uploads": self.config["upload_dir"],
                "results": self.config["result_dir"],
                "temp": self.config["temp_dir"]
            }
            
            for name, directory in directories.items():
                path = Path(directory)
                if path.exists():
                    files = list(path.iterdir())
                    total_size = sum(f.stat().st_size for f in files if f.is_file())
                    
                    stats[name] = {
                        "file_count": len([f for f in files if f.is_file()]),
                        "total_size": total_size,
                        "total_size_mb": round(total_size / (1024 * 1024), 2)
                    }
                else:
                    stats[name] = {"file_count": 0, "total_size": 0, "total_size_mb": 0}
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في حساب إحصائيات التخزين: {e}")
            return {}
