"""
Configuración de Celery para tareas en segundo plano.
"""
from celery import Celery
from app.core.config import settings

# Crear instancia de Celery
celery_app = Celery(
    'virtual_assistant',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.worker.tasks'
    ]
)

# Configuración de Celery
celery_app.conf.update(
    result_expires=3600,  # Los resultados expiran después de 1 hora
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Configuración de rutas de tareas
    task_routes={
        'app.worker.tasks.process_audio_task': {'queue': 'audio'},
        'app.worker.tasks.send_email_task': {'queue': 'email'},
        'app.worker.tasks.analyze_text_task': {'queue': 'analysis'},
    },
    
    # Configuración de periodicidad (beat)
    beat_schedule={
        'cleanup-old-files-every-day': {
            'task': 'app.worker.tasks.cleanup_old_files',
            'schedule': 86400.0,  # Cada 24 horas
        },
        'backup-database-every-week': {
            'task': 'app.worker.tasks.backup_database',
            'schedule': 604800.0,  # Cada 7 días
        },
    }
)

# Configuración específica por entorno
if settings.ENVIRONMENT == 'development':
    celery_app.conf.update(
        task_always_eager=False,  # No ejecutar sincrónicamente en desarrollo
        task_eager_propagates=True,
    )
elif settings.ENVIRONMENT == 'production':
    celery_app.conf.update(
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_track_started=True,
    )

if __name__ == '__main__':
    celery_app.start()