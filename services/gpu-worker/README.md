# GPU Worker Service

خدمة معالجة الصور باستخدام Flux Dev + LoRA لرفع جودة الصور.

## 🎯 الوظائف الرئيسية

- رفع جودة الصور باستخدام Flux Dev + LoRA
- API endpoints لمعالجة الصور
- مراقبة استخدام GPU والذاكرة
- نظام مقاييس الأداء
- إدارة الملفات والتنظيف التلقائي

## 🏗️ الهيكل

```
gpu-worker/
├── app.py                 # التطبيق الرئيسي
├── core/                  # المكونات الأساسية
│   ├── config.py         # الإعدادات
│   ├── models.py         # نماذج البيانات
│   ├── upscaler.py       # معالج الصور
│   └── monitoring.py     # نظام المراقبة
├── utils/                 # الأدوات المساعدة
│   ├── file_handler.py   # معالج الملفات
│   └── gpu_monitor.py    # مراقب GPU
├── tests/                 # الاختبارات
└── requirements.txt       # المتطلبات
```

## 🚀 التشغيل

### محلياً (للتطوير):
```bash
cd services/gpu-worker
pip install -r requirements.txt
python app.py
```

### باستخدام Docker:
```bash
# من المجلد الرئيسي
docker-compose up gpu-worker
```

## 📡 API Endpoints

### الصحة والحالة
- `GET /health` - فحص صحة الخدمة
- `GET /status` - حالة الخدمة التفصيلية
- `GET /metrics` - مقاييس الأداء

### معالجة الصور
- `POST /upscale` - رفع جودة الصورة

#### مثال على الاستخدام:
```bash
curl -X POST "http://localhost:8001/upscale" \
  -F "file=@image.jpg" \
  -F "prompt=high quality, detailed, sharp"
```

## ⚙️ الإعدادات

يمكن تخصيص الإعدادات عبر متغيرات البيئة:

```bash
# إعدادات الخادم
HOST=0.0.0.0
PORT=8000
DEBUG=false

# إعدادات الموديل
MODEL_PATH=/app/models
FLUX_MODEL_NAME=black-forest-labs/FLUX.1-dev
LORA_MODEL_PATH=/app/models/lora_upscaler.safetensors

# إعدادات GPU
CUDA_DEVICE=0
ENABLE_MEMORY_EFFICIENT=true

# إعدادات المعالجة
MAX_IMAGE_SIZE=2048
MAX_FILE_SIZE=10485760
NUM_INFERENCE_STEPS=20
GUIDANCE_SCALE=7.5
```

## 🧪 الاختبارات

```bash
# تشغيل الاختبارات
cd services/gpu-worker
python -m pytest tests/ -v

# اختبار محدد
python -m pytest tests/test_basic.py::TestGPUWorkerBasic::test_health_endpoint -v
```

## 📊 المراقبة

### Prometheus Metrics
- `gpu_worker_requests_total` - إجمالي الطلبات
- `gpu_worker_processing_time_seconds` - وقت المعالجة
- `gpu_worker_gpu_memory_usage_bytes` - استخدام ذاكرة GPU
- `gpu_worker_images_processed_total` - الصور المعالجة

### Health Checks
```bash
# فحص سريع
curl http://localhost:8001/health

# حالة مفصلة
curl http://localhost:8001/status

# مقاييس الأداء
curl http://localhost:8001/metrics
```

## 🔧 استكشاف الأخطاء

### مشاكل شائعة:

1. **CUDA غير متوفر**
   ```bash
   # التحقق من CUDA
   nvidia-smi
   python -c "import torch; print(torch.cuda.is_available())"
   ```

2. **نفاد ذاكرة GPU**
   ```bash
   # مراقبة استخدام الذاكرة
   watch -n 1 nvidia-smi
   ```

3. **بطء في المعالجة**
   - تأكد من تفعيل `ENABLE_MEMORY_EFFICIENT=true`
   - قلل من `NUM_INFERENCE_STEPS`
   - تحقق من درجة حرارة GPU

### السجلات:
```bash
# عرض السجلات
docker-compose logs gpu-worker -f

# السجلات مع الوقت
docker-compose logs gpu-worker -f --timestamps
```

## 🔒 الأمان

- التحقق من صيغة وحجم الملفات المرفوعة
- تنظيف تلقائي للملفات المؤقتة
- حدود زمنية للمعالجة
- مراقبة استخدام الموارد

## 📈 الأداء

### المتطلبات الموصى بها:
- GPU: RTX 3090/4090 أو أفضل
- VRAM: 24GB+
- RAM: 32GB+
- Storage: SSD سريع

### التحسينات:
- Memory efficient attention
- Model CPU offloading
- Attention slicing
- تنظيف دوري للذاكرة

## 🔄 التطوير

### إضافة ميزات جديدة:
1. أضف endpoint جديد في `app.py`
2. أضف نموذج البيانات في `core/models.py`
3. أضف المنطق في `core/upscaler.py`
4. أضف اختبارات في `tests/`

### أفضل الممارسات:
- استخدم type hints
- أضف docstrings
- اكتب اختبارات
- راقب الأداء
- سجل الأخطاء بوضوح
