"""
Endpoints para gestión del sistema y monitoreo.
"""
from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import os
import logging

from app.models.schemas import HealthCheck
from app.services.ai.openai_service import OpenAIService, get_openai_service
from app.services.ai.voice_service import VoiceService, get_voice_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthCheck)
async def health_check(
    openai_service: OpenAIService = Depends(get_openai_service),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Verificar el estado de salud del servicio y sus dependencias.
    
    Returns:
        Estado de salud del sistema y servicios dependientes
    """
    try:
        # Verificar servicios externos
        openai_health = await openai_service.health_check()
        voice_health = await voice_service.health_check()
        
        # Verificar recursos del sistema
        system_status = "healthy"
        details = {}
        
        # Uso de CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        details["cpu_usage"] = f"{cpu_percent}%"
        if cpu_percent > 90:
            system_status = "degraded"
        
        # Uso de memoria
        memory = psutil.virtual_memory()
        details["memory_usage"] = f"{memory.percent}%"
        if memory.percent > 90:
            system_status = "degraded"
        
        # Uso de disco
        disk = psutil.disk_usage('/')
        details["disk_usage"] = f"{disk.percent}%"
        if disk.percent > 90:
            system_status = "degraded"
        
        # Estado general
        overall_status = "healthy"
        if not openai_health or not voice_health:
            overall_status = "unhealthy"
        elif system_status == "degraded":
            overall_status = "degraded"
        
        return HealthCheck(
            status=overall_status,
            service="virtual-assistant",
            version="1.0.0",
            timestamp=datetime.now(),
            details={
                "openai_service": "healthy" if openai_health else "unhealthy",
                "voice_service": "healthy" if voice_health else "unhealthy",
                "system": system_status,
                **details
            }
        )
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        return HealthCheck(
            status="unhealthy",
            service="virtual-assistant",
            version="1.0.0",
            timestamp=datetime.now(),
            details={"error": str(e)}
        )

@router.get("/info")
async def system_info():
    """
    Obtener información del sistema y configuración.
    
    Returns:
        Información detallada del sistema y configuración
    """
    # Información del sistema
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "service": "Virtual Assistant API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "timestamp": datetime.now(),
        "system": {
            "cpu_cores": psutil.cpu_count(),
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_total": f"{memory.total // (1024**3)}GB",
            "memory_used": f"{memory.used // (1024**3)}GB",
            "memory_usage": f"{memory.percent}%",
            "disk_total": f"{disk.total // (1024**3)}GB",
            "disk_used": f"{disk.used // (1024**3)}GB",
            "disk_usage": f"{disk.percent}%"
        },
        "features": [
            "Chat inteligente con IA",
            "Reconocimiento de voz (STT)",
            "Síntesis de voz (TTS)",
            "API RESTful",
            "Interfaz gráfica"
        ],
        "supported_ai_models": [
            "gpt-4",
            "gpt-3.5-turbo",
            "whisper-1"
        ],
        "supported_languages": ["es", "en"],
        "max_file_size": "5MB",
        "rate_limit": "60 requests/minuto"
    }

@router.get("/stats")
async def system_stats():
    """
    Obtener estadísticas de uso del servicio.
    
    Returns:
        Estadísticas de uso y rendimiento
    """
    # Aquí podrías agregar métricas de tu aplicación
    from app.api.endpoints.chat import conversations
    
    return {
        "conversations_active": len(conversations),
        "total_messages": sum(len(conv["messages"]) for conv in conversations.values()),
        "timestamp": datetime.now(),
        "uptime": psutil.boot_time(),
        "active_processes": len(psutil.pids())
    }

@router.get("/config")
async def get_config():
    """
    Obtener configuración actual del servicio (sin valores sensibles).
    
    Returns:
        Configuración no sensible del servicio
    """
    from app.core.config import settings
    
    return {
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "assistant_name": settings.ASSISTANT_NAME,
        "default_language": settings.DEFAULT_LANGUAGE,
        "max_tokens": settings.MAX_TOKENS,
        "audio_sample_rate": settings.AUDIO_SAMPLE_RATE,
        "supported_models": {
            "ai": settings.DEFAULT_AI_MODEL,
            "stt": settings.DEFAULT_STT_MODEL,
            "tts": settings.DEFAULT_VOICE_MODEL
        }
    }