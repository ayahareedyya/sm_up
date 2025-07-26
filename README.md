# SM_UP - AI Image Upscaler

مشروع لرفع جودة الصور باستخدام Flux Dev + LoRA مع واجهة ويب ونظام دفع.

## 🏗️ هيكل المشروع

```
sm_up/
├── services/
│   ├── gpu-worker/          # خدمة معالجة الصور
│   ├── api-gateway/         # API الرئيسي
│   ├── frontend/            # واجهة المستخدم
│   └── database/            # قاعدة البيانات
├── shared/                  # مكتبات مشتركة
├── tests/                   # اختبارات
├── scripts/                 # أدوات النشر
└── environments/            # إعدادات البيئات
```

## 🚀 أوامر سريعة

```bash
# تطوير محلي
make dev

# نشر على RunPod
make deploy

# تشغيل الاختبارات
make test
```

## 📋 خطة التطوير

- [x] إعداد المشروع الأساسي
- [ ] GPU Worker
- [ ] API Gateway
- [ ] Frontend
- [ ] نظام الدفع
- [ ] النشر النهائي

## 🔧 متطلبات التشغيل

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- GPU مع CUDA support

---
تم إنشاؤه بواسطة [ayahareedyya](https://github.com/ayahareedyya)
