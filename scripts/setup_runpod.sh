#!/bin/bash

# SM_UP - سكريبت إعداد RunPod
# يقوم بإعداد البيئة وتثبيت المتطلبات على RunPod

set -e  # إيقاف عند أي خطأ

echo "🚀 بدء إعداد SM_UP على RunPod..."

# ألوان للطباعة
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# دالة للطباعة الملونة
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

# التحقق من وجود CUDA
check_cuda() {
    print_status "التحقق من CUDA..."
    
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi
        print_success "CUDA متوفر"
    else
        print_error "CUDA غير متوفر!"
        exit 1
    fi
}

# تحديث النظام
update_system() {
    print_status "تحديث النظام..."
    
    apt-get update -y
    apt-get upgrade -y
    
    print_success "تم تحديث النظام"
}

# تثبيت Docker
install_docker() {
    print_status "تثبيت Docker..."
    
    if command -v docker &> /dev/null; then
        print_warning "Docker مثبت بالفعل"
        return
    fi
    
    # تثبيت Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    
    # إضافة المستخدم لمجموعة docker
    usermod -aG docker $USER
    
    # تشغيل Docker
    systemctl start docker
    systemctl enable docker
    
    print_success "تم تثبيت Docker"
}

# تثبيت Docker Compose
install_docker_compose() {
    print_status "تثبيت Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose مثبت بالفعل"
        return
    fi
    
    # تحميل Docker Compose
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # إعطاء صلاحيات التنفيذ
    chmod +x /usr/local/bin/docker-compose
    
    # إنشاء رابط رمزي
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    print_success "تم تثبيت Docker Compose"
}

# تثبيت NVIDIA Container Toolkit
install_nvidia_docker() {
    print_status "تثبيت NVIDIA Container Toolkit..."
    
    # إضافة مستودع NVIDIA
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
    
    # تحديث وتثبيت
    apt-get update
    apt-get install -y nvidia-docker2
    
    # إعادة تشغيل Docker
    systemctl restart docker
    
    print_success "تم تثبيت NVIDIA Container Toolkit"
}

# تثبيت أدوات إضافية
install_tools() {
    print_status "تثبيت أدوات إضافية..."
    
    apt-get install -y \
        curl \
        wget \
        git \
        htop \
        tree \
        unzip \
        vim \
        nano \
        screen \
        tmux \
        python3-pip
    
    print_success "تم تثبيت الأدوات الإضافية"
}

# إنشاء مجلدات العمل
create_directories() {
    print_status "إنشاء مجلدات العمل..."
    
    mkdir -p /workspace/sm_up
    mkdir -p /workspace/sm_up/data/{uploads,results,temp}
    mkdir -p /workspace/sm_up/models
    mkdir -p /workspace/logs
    
    # إعطاء صلاحيات
    chmod -R 755 /workspace
    
    print_success "تم إنشاء مجلدات العمل"
}

# إعداد متغيرات البيئة
setup_environment() {
    print_status "إعداد متغيرات البيئة..."
    
    # إنشاء ملف .env إذا لم يكن موجوداً
    if [ ! -f /workspace/sm_up/.env ]; then
        cp /workspace/sm_up/.env.example /workspace/sm_up/.env 2>/dev/null || true
    fi
    
    # إضافة متغيرات إلى bashrc
    echo 'export WORKSPACE="/workspace"' >> ~/.bashrc
    echo 'export SM_UP_PATH="/workspace/sm_up"' >> ~/.bashrc
    echo 'alias sm_up="cd /workspace/sm_up"' >> ~/.bashrc
    echo 'alias sm_logs="docker-compose logs -f"' >> ~/.bashrc
    echo 'alias sm_status="docker-compose ps"' >> ~/.bashrc
    
    print_success "تم إعداد متغيرات البيئة"
}

# اختبار التثبيت
test_installation() {
    print_status "اختبار التثبيت..."
    
    # اختبار Docker
    if docker --version; then
        print_success "Docker يعمل بشكل صحيح"
    else
        print_error "مشكلة في Docker"
        exit 1
    fi
    
    # اختبار Docker Compose
    if docker-compose --version; then
        print_success "Docker Compose يعمل بشكل صحيح"
    else
        print_error "مشكلة في Docker Compose"
        exit 1
    fi
    
    # اختبار NVIDIA Docker
    if docker run --rm --gpus all nvidia/cuda:11.8-base-ubuntu22.04 nvidia-smi; then
        print_success "NVIDIA Docker يعمل بشكل صحيح"
    else
        print_warning "قد تكون هناك مشكلة في NVIDIA Docker"
    fi
}

# عرض معلومات النظام
show_system_info() {
    print_status "معلومات النظام:"
    
    echo "نظام التشغيل: $(lsb_release -d | cut -f2)"
    echo "المعالج: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
    echo "الذاكرة: $(free -h | grep '^Mem:' | awk '{print $2}')"
    echo "القرص الصلب: $(df -h / | tail -1 | awk '{print $2}')"
    
    if command -v nvidia-smi &> /dev/null; then
        echo "GPU:"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits
    fi
}

# الدالة الرئيسية
main() {
    print_status "بدء إعداد SM_UP على RunPod..."
    
    # التحقق من الصلاحيات
    if [ "$EUID" -ne 0 ]; then
        print_error "يجب تشغيل هذا السكريبت بصلاحيات root"
        exit 1
    fi
    
    # تنفيذ خطوات الإعداد
    check_cuda
    update_system
    install_tools
    install_docker
    install_docker_compose
    install_nvidia_docker
    create_directories
    setup_environment
    test_installation
    show_system_info
    
    print_success "✅ تم إعداد SM_UP بنجاح!"
    print_status "يمكنك الآن:"
    print_status "1. رفع كود المشروع إلى /workspace/sm_up"
    print_status "2. تشغيل: cd /workspace/sm_up && docker-compose up -d"
    print_status "3. مراقبة السجلات: docker-compose logs -f"
}

# تشغيل الدالة الرئيسية
main "$@"
