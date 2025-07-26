# Environment Configurations

إعدادات البيئات المختلفة لتطبيق SM_UP.

## 📁 البيئات المتاحة

### `development/`
- بيئة التطوير المحلي
- إعدادات مبسطة للاختبار
- قاعدة بيانات محلية
- مفاتيح اختبار للخدمات الخارجية

### `staging/`
- بيئة التجريب
- مشابهة للإنتاج لكن مع بيانات اختبار
- للاختبار النهائي قبل النشر

### `production/`
- بيئة الإنتاج
- إعدادات آمنة ومحسنة
- مفاتيح حقيقية للخدمات

## 🔧 الاستخدام

### تشغيل بيئة محددة:
```bash
# Development
cp environments/development/.env .env
docker-compose up

# Staging  
cp environments/staging/.env .env
docker-compose up

# Production
cp environments/production/.env .env
docker-compose up -d
```

### أو باستخدام docker-compose مع ملف محدد:
```bash
# Development
docker-compose --env-file environments/development/.env up

# Production
docker-compose --env-file environments/production/.env up -d
```

## ⚠️ تحذيرات أمنية

1. **لا تضع مفاتيح حقيقية في Git**
2. **غير كلمات المرور الافتراضية**
3. **استخدم متغيرات البيئة للمعلومات الحساسة**
4. **راجع الإعدادات قبل النشر**

## 🔐 المتغيرات الحساسة

يجب تغيير هذه المتغيرات في الإنتاج:
- `POSTGRES_PASSWORD`
- `API_SECRET_KEY`
- `JWT_SECRET_KEY`
- `PAYMOB_API_KEY`
- `SMTP_PASSWORD`
- `SENTRY_DSN`
