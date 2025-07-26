#!/bin/bash

# SM_UP - سكريبت النشر
# ينشر التطبيق على RunPod

set -e

echo "🚀 بدء نشر SM_UP..."

# ألوان للطباعة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# التحقق من المتطلبات
check_requirements() {
    print_status "التحقق من المتطلبات..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker غير مثبت"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose غير مثبت"
        exit 1
    fi
    
    if [ ! -f "docker-compose.yml" ]; then
        print_error "ملف docker-compose.yml غير موجود"
        exit 1
    fi
    
    print_success "جميع المتطلبات متوفرة"
}

# إيقاف الخدمات الحالية
stop_services() {
    print_status "إيقاف الخدمات الحالية..."
    
    docker-compose down || true
    
    print_success "تم إيقاف الخدمات"
}

# بناء الصور
build_images() {
    print_status "بناء صور Docker..."
    
    docker-compose build --no-cache
    
    print_success "تم بناء الصور"
}

# تشغيل الخدمات
start_services() {
    print_status "تشغيل الخدمات..."
    
    docker-compose up -d
    
    print_success "تم تشغيل الخدمات"
}

# انتظار جاهزية الخدمات
wait_for_services() {
    print_status "انتظار جاهزية الخدمات..."
    
    # انتظار GPU Worker
    for i in {1..30}; do
        if curl -f http://localhost:8001/health &> /dev/null; then
            print_success "GPU Worker جاهز"
            break
        fi
        
        if [ $i -eq 30 ]; then
            print_error "GPU Worker لم يصبح جاهزاً"
            exit 1
        fi
        
        sleep 2
    done
    
    # انتظار API Gateway (عندما يتم تطويره)
    # for i in {1..30}; do
    #     if curl -f http://localhost:8000/health &> /dev/null; then
    #         print_success "API Gateway جاهز"
    #         break
    #     fi
    #     sleep 2
    # done
}

# اختبار النشر
test_deployment() {
    print_status "اختبار النشر..."
    
    # اختبار GPU Worker
    if curl -f http://localhost:8001/health; then
        print_success "GPU Worker يعمل بشكل صحيح"
    else
        print_error "مشكلة في GPU Worker"
        return 1
    fi
    
    # عرض حالة الخدمات
    print_status "حالة الخدمات:"
    docker-compose ps
}

# عرض السجلات
show_logs() {
    print_status "آخر السجلات:"
    docker-compose logs --tail=20
}

# عرض معلومات النشر
show_deployment_info() {
    print_success "✅ تم نشر SM_UP بنجاح!"
    echo ""
    print_status "الخدمات المتاحة:"
    echo "  - GPU Worker: http://localhost:8001"
    echo "  - Health Check: http://localhost:8001/health"
    echo "  - Status: http://localhost:8001/status"
    echo "  - Metrics: http://localhost:8001/metrics"
    echo ""
    print_status "أوامر مفيدة:"
    echo "  - عرض السجلات: docker-compose logs -f"
    echo "  - حالة الخدمات: docker-compose ps"
    echo "  - إيقاف الخدمات: docker-compose down"
    echo "  - إعادة التشغيل: docker-compose restart"
}

# تنظيف في حالة الفشل
cleanup_on_failure() {
    print_error "فشل في النشر، جاري التنظيف..."
    docker-compose down || true
    exit 1
}

# الدالة الرئيسية
main() {
    # إعداد معالج الأخطاء
    trap cleanup_on_failure ERR
    
    print_status "بدء عملية النشر..."
    
    check_requirements
    stop_services
    build_images
    start_services
    wait_for_services
    
    if test_deployment; then
        show_deployment_info
    else
        print_error "فشل في اختبار النشر"
        show_logs
        exit 1
    fi
}

# تشغيل الدالة الرئيسية
main "$@"
