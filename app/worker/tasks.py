"""
Tareas en segundo plano para Celery.
"""
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.worker.celery import celery_app
from app.services.ai.openai_service import OpenAIService
from app.services.email_service import email_service
from app.core.config import settings

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='process_audio_task')
def process_audio_task(self, audio_file_path: str, user_id: Optional[int] = None):
    """
    Tarea para procesamiento de audio en segundo plano.
    
    Args:
        audio_file_path: Ruta al archivo de audio
        user_id: ID del usuario (opcional)
    """
    try:
        logger.info(f"Iniciando procesamiento de audio: {audio_file_path}")
        
        # Actualizar estado de la tarea
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Transcribiendo audio...'}
        )
        
        # Transcribir audio
        openai_service = OpenAIService()
        transcription = openai_service.transcribe_audio(audio_file_path)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 50, 'total': 100, 'status': 'Procesando texto...'}
        )
        
        # Procesar el texto transcribido (aquí podrías hacer análisis adicional)
        processed_text = transcription.upper()  # Ejemplo simple
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 100, 'total': 100, 'status': 'Completado'}
        )
        
        logger.info(f"Procesamiento de audio completado: {audio_file_path}")
        
        return {
            'success': True,
            'transcription': transcription,
            'processed_text': processed_text,
            'user_id': user_id
        }
        
    except Exception as e:
        logger.error(f"Error en procesamiento de audio: {e}")
        
        # Notificar error por email si está configurado
        if settings.EMAIL_ENABLED and settings.SMTP_USER:
            email_service.send_error_notification(
                [settings.SMTP_USER],
                f"Error procesando audio: {audio_file_path}",
                str(e)
            )
        
        return {
            'success': False,
            'error': str(e),
            'user_id': user_id
        }

@celery_app.task(name='send_email_task')
def send_email_task(to_emails: list, subject: str, body: str, is_html: bool = False):
    """
    Tarea para envío de emails en segundo plano.
    
    Args:
        to_emails: Lista de direcciones de email
        subject: Asunto del email
        body: Cuerpo del email
        is_html: Si el cuerpo es HTML
    """
    try:
        logger.info(f"Enviando email a {to_emails}: {subject}")
        
        success = email_service.send_email(to_emails, subject, body, is_html)
        
        if success:
            logger.info("Email enviado correctamente")
            return {'success': True, 'sent_to': to_emails}
        else:
            logger.error("Error enviando email")
            return {'success': False, 'sent_to': to_emails}
            
    except Exception as e:
        logger.error(f"Error en tarea de envío de email: {e}")
        return {'success': False, 'error': str(e)}

@celery_app.task(name='analyze_text_task')
def analyze_text_task(text: str, analysis_type: str = 'sentiment'):
    """
    Tarea para análisis de texto en segundo plano.
    
    Args:
        text: Texto a analizar
        analysis_type: Tipo de análisis ('sentiment', 'keywords', 'summary')
    """
    try:
        logger.info(f"Analizando texto (tipo: {analysis_type}), longitud: {len(text)}")
        
        openai_service = OpenAIService()
        
        # Dependiendo del tipo de análisis, construir el prompt
        if analysis_type == 'sentiment':
            prompt = f"Analiza el sentimiento del siguiente texto y devuelve solo una de estas opciones: POSITIVO, NEGATIVO, NEUTRO. Texto: {text}"
        elif analysis_type == 'keywords':
            prompt = f"Extrae las 5 palabras clave más importantes del siguiente texto. Devuélvelas como una lista separada por comas. Texto: {text}"
        elif analysis_type == 'summary':
            prompt = f"Resume el siguiente texto en un párrafo conciso. Texto: {text}"
        else:
            return {'success': False, 'error': f'Tipo de análisis no válido: {analysis_type}'}
        
        # Usar OpenAI para el análisis
        messages = [
            {"role": "system", "content": "Eres un asistente especializado en análisis de texto."},
            {"role": "user", "content": prompt}
        ]
        
        result = openai_service.chat_completion(messages)
        
        return {
            'success': True,
            'analysis_type': analysis_type,
            'result': result,
            'text_length': len(text)
        }
        
    except Exception as e:
        logger.error(f"Error en análisis de texto: {e}")
        return {'success': False, 'error': str(e)}

@celery_app.task(name='cleanup_old_files')
def cleanup_old_files(days_old: int = 7):
    """
    Tarea para limpiar archivos antiguos.
    
    Args:
        days_old: Número de días para considerar un archivo como antiguo
    """
    try:
        logger.info(f"Limpiando archivos más antiguos de {days_old} días")
        
        upload_path = Path(settings.UPLOAD_FOLDER)
        cutoff_time = datetime.now() - timedelta(days=days_old)
        deleted_files = 0
        total_size = 0
        
        for file_path in upload_path.rglob('*'):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if file_time < cutoff_time:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_files += 1
                    total_size += file_size
                    logger.debug(f"Eliminado: {file_path}")
        
        logger.info(f"Limpieza completada: {deleted_files} archivos eliminados, {total_size} bytes liberados")
        
        return {
            'success': True,
            'deleted_files': deleted_files,
            'freed_space': total_size,
            'cutoff_time': cutoff_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error en limpieza de archivos: {e}")
        return {'success': False, 'error': str(e)}

@celery_app.task(name='backup_database')
def backup_database():
    """
    Tarea para realizar backup de la base de datos.
    """
    try:
        logger.info("Iniciando backup de base de datos")
        
        # Aquí implementarías la lógica de backup específica de tu base de datos
        # Esto es un ejemplo genérico
        
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'database_backup_{timestamp}.sql'
        
        # Ejemplo para PostgreSQL usando pg_dump
        # import subprocess
        # result = subprocess.run(['pg_dump', settings.DATABASE_URL], stdout=open(backup_file, 'w'))
        
        # Por ahora, simular un backup exitoso
        with open(backup_file, 'w') as f:
            f.write(f"-- Backup de base de datos - {timestamp}\n")
            f.write("-- Esta es una simulación del backup\n")
        
        file_size = backup_file.stat().st_size
        
        logger.info(f"Backup completado: {backup_file}, tamaño: {file_size} bytes")
        
        return {
            'success': True,
            'backup_file': str(backup_file),
            'file_size': file_size,
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"Error en backup de base de datos: {e}")
        return {'success': False, 'error': str(e)}