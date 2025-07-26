"""
اختبارات أساسية لـ GPU Worker Service
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import tempfile
import os
from PIL import Image

# Import the app
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app
from core.config import settings
from utils.file_handler import FileHandler
from utils.gpu_monitor import GPUMonitor


class TestGPUWorkerBasic:
    """اختبارات أساسية"""
    
    @pytest.fixture
    def client(self):
        """عميل الاختبار"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """اختبار endpoint الصحة"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "gpu_available" in data
    
    def test_status_endpoint(self, client):
        """اختبار endpoint الحالة"""
        response = client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "service" in data
        assert data["service"] == "gpu-worker"
    
    def test_metrics_endpoint(self, client):
        """اختبار endpoint المقاييس"""
        response = client.get("/metrics")
        assert response.status_code == 200


class TestFileHandler:
    """اختبارات معالج الملفات"""
    
    @pytest.fixture
    def file_handler(self):
        """معالج الملفات للاختبار"""
        return FileHandler()
    
    @pytest.fixture
    def test_image(self):
        """صورة اختبار"""
        # إنشاء صورة اختبار
        img = Image.new('RGB', (100, 100), color='red')
        
        # حفظ في ملف مؤقت
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name, 'PNG')
        temp_file.close()
        
        yield temp_file.name
        
        # تنظيف
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    @pytest.mark.asyncio
    async def test_validate_image(self, file_handler, test_image):
        """اختبار التحقق من الصورة"""
        result = await file_handler.validate_image(test_image)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_invalid_image(self, file_handler):
        """اختبار التحقق من ملف غير صحيح"""
        # إنشاء ملف نصي
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b"This is not an image")
        temp_file.close()
        
        try:
            result = await file_handler.validate_image(temp_file.name)
            assert result is False
        finally:
            os.unlink(temp_file.name)
    
    def test_get_file_info(self, file_handler, test_image):
        """اختبار الحصول على معلومات الملف"""
        info = file_handler.get_file_info(test_image)
        
        assert info is not None
        assert "size" in info
        assert "width" in info
        assert "height" in info
        assert info["width"] == 100
        assert info["height"] == 100
    
    def test_storage_stats(self, file_handler):
        """اختبار إحصائيات التخزين"""
        stats = file_handler.get_storage_stats()
        
        assert isinstance(stats, dict)
        assert "uploads" in stats
        assert "results" in stats
        assert "temp" in stats


class TestGPUMonitor:
    """اختبارات مراقب GPU"""
    
    @pytest.fixture
    def gpu_monitor(self):
        """مراقب GPU للاختبار"""
        return GPUMonitor()
    
    def test_get_gpu_status(self, gpu_monitor):
        """اختبار حالة GPU"""
        status = gpu_monitor.get_gpu_status()
        
        assert isinstance(status, dict)
        assert "available" in status
        assert "device_count" in status
    
    def test_get_memory_usage(self, gpu_monitor):
        """اختبار استخدام الذاكرة"""
        memory = gpu_monitor.get_memory_usage()
        
        assert isinstance(memory, dict)
        assert "total" in memory
        assert "used" in memory
        assert "percent" in memory
    
    def test_get_system_stats(self, gpu_monitor):
        """اختبار إحصائيات النظام"""
        stats = gpu_monitor.get_system_stats()
        
        assert isinstance(stats, dict)
        assert "cpu" in stats
        assert "memory" in stats
        assert "disk" in stats
        assert "gpu" in stats
    
    def test_check_gpu_health(self, gpu_monitor):
        """اختبار فحص صحة GPU"""
        health = gpu_monitor.check_gpu_health()
        
        assert isinstance(health, dict)
        assert "healthy" in health
        assert "warnings" in health
        assert "errors" in health


class TestConfiguration:
    """اختبارات الإعدادات"""
    
    def test_settings_loaded(self):
        """اختبار تحميل الإعدادات"""
        assert settings.HOST is not None
        assert settings.PORT is not None
        assert settings.MODEL_PATH is not None
    
    def test_model_config(self):
        """اختبار إعدادات الموديل"""
        from core.config import get_model_config
        
        config = get_model_config()
        assert isinstance(config, dict)
        assert "flux_model" in config
        assert "device" in config
    
    def test_processing_config(self):
        """اختبار إعدادات المعالجة"""
        from core.config import get_processing_config
        
        config = get_processing_config()
        assert isinstance(config, dict)
        assert "num_inference_steps" in config
        assert "guidance_scale" in config
    
    def test_file_config(self):
        """اختبار إعدادات الملفات"""
        from core.config import get_file_config
        
        config = get_file_config()
        assert isinstance(config, dict)
        assert "upload_dir" in config
        assert "result_dir" in config


if __name__ == "__main__":
    # تشغيل الاختبارات
    pytest.main([__file__, "-v"])
