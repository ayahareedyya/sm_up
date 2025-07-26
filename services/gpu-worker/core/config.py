"""
إعدادات GPU Worker Service
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """إعدادات التطبيق"""
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Host address")
    PORT: int = Field(default=8000, description="Port number")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Model settings
    MODEL_PATH: str = Field(default="/app/models", description="Path to models directory")
    FLUX_MODEL_NAME: str = Field(default="black-forest-labs/FLUX.1-dev", description="Flux model name")
    LORA_MODEL_PATH: str = Field(default="/app/models/lora_upscaler.safetensors", description="LoRA model path")
    
    # Processing settings
    MAX_IMAGE_SIZE: int = Field(default=2048, description="Maximum image dimension")
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum file size in bytes (10MB)")
    SUPPORTED_FORMATS: list = Field(default=["JPEG", "PNG", "WEBP"], description="Supported image formats")
    
    # GPU settings
    CUDA_DEVICE: str = Field(default="0", description="CUDA device ID")
    MAX_BATCH_SIZE: int = Field(default=1, description="Maximum batch size")
    ENABLE_MEMORY_EFFICIENT: bool = Field(default=True, description="Enable memory efficient attention")
    
    # File paths
    UPLOAD_DIR: str = Field(default="/app/data/uploads", description="Upload directory")
    RESULT_DIR: str = Field(default="/app/data/results", description="Results directory")
    TEMP_DIR: str = Field(default="/app/data/temp", description="Temporary directory")
    
    # Processing timeouts
    PROCESSING_TIMEOUT: int = Field(default=300, description="Processing timeout in seconds")
    CLEANUP_INTERVAL: int = Field(default=3600, description="Cleanup interval in seconds")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=8001, description="Metrics port")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    LOG_FORMAT: str = Field(
        default="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        description="Log format"
    )
    
    # Default prompts
    DEFAULT_UPSCALE_PROMPT: str = Field(
        default="high quality, detailed, sharp, professional photography, 4k, ultra high resolution",
        description="Default upscale prompt"
    )
    NEGATIVE_PROMPT: str = Field(
        default="blurry, low quality, pixelated, compressed, artifacts, noise",
        description="Negative prompt"
    )
    
    # Generation parameters
    NUM_INFERENCE_STEPS: int = Field(default=20, description="Number of inference steps")
    GUIDANCE_SCALE: float = Field(default=7.5, description="Guidance scale")
    STRENGTH: float = Field(default=0.8, description="Denoising strength")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


def get_model_config() -> dict:
    """إعدادات الموديل"""
    return {
        "flux_model": settings.FLUX_MODEL_NAME,
        "lora_path": settings.LORA_MODEL_PATH,
        "device": f"cuda:{settings.CUDA_DEVICE}",
        "enable_memory_efficient": settings.ENABLE_MEMORY_EFFICIENT,
        "max_batch_size": settings.MAX_BATCH_SIZE
    }


def get_processing_config() -> dict:
    """إعدادات المعالجة"""
    return {
        "num_inference_steps": settings.NUM_INFERENCE_STEPS,
        "guidance_scale": settings.GUIDANCE_SCALE,
        "strength": settings.STRENGTH,
        "default_prompt": settings.DEFAULT_UPSCALE_PROMPT,
        "negative_prompt": settings.NEGATIVE_PROMPT
    }


def get_file_config() -> dict:
    """إعدادات الملفات"""
    return {
        "upload_dir": settings.UPLOAD_DIR,
        "result_dir": settings.RESULT_DIR,
        "temp_dir": settings.TEMP_DIR,
        "max_file_size": settings.MAX_FILE_SIZE,
        "max_image_size": settings.MAX_IMAGE_SIZE,
        "supported_formats": settings.SUPPORTED_FORMATS
    }
