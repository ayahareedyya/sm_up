# SM_UP Makefile - أوامر مبسطة للتطوير والنشر

.PHONY: help dev build test deploy clean logs backup

# عرض المساعدة
help:
	@echo "SM_UP - أوامر متاحة:"
	@echo ""
	@echo "  make dev      - تشغيل التطبيق للتطوير"
	@echo "  make build    - بناء جميع الصور"
	@echo "  make test     - تشغيل الاختبارات"
	@echo "  make deploy   - نشر على الإنتاج"
	@echo "  make logs     - عرض السجلات"
	@echo "  make clean    - تنظيف الملفات المؤقتة"
	@echo "  make backup   - نسخ احتياطي"
	@echo ""

# تشغيل للتطوير
dev:
	@echo "🚀 تشغيل SM_UP للتطوير..."
	docker-compose up --build

# بناء جميع الصور
build:
	@echo "🔨 بناء جميع الصور..."
	docker-compose build

# تشغيل الاختبارات
test:
	@echo "🧪 تشغيل الاختبارات..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# نشر على الإنتاج
deploy:
	@echo "🚀 نشر على الإنتاج..."
	./scripts/deploy.sh

# عرض السجلات
logs:
	@echo "📋 عرض السجلات..."
	docker-compose logs -f

# تنظيف الملفات المؤقتة
clean:
	@echo "🧹 تنظيف الملفات المؤقتة..."
	docker-compose down -v
	docker system prune -f
	rm -rf data/temp/*

# نسخ احتياطي
backup:
	@echo "💾 إنشاء نسخ احتياطي..."
	./scripts/backup.sh

# إيقاف جميع الخدمات
stop:
	@echo "⏹️ إيقاف جميع الخدمات..."
	docker-compose down

# إعادة تشغيل
restart:
	@echo "🔄 إعادة تشغيل..."
	docker-compose restart

# عرض حالة الخدمات
status:
	@echo "📊 حالة الخدمات:"
	docker-compose ps
