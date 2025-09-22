"""
Endpoints para procesamiento de voz (STT y TTS).
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Optional
import logging
import base64
import tempfile
import os
from pathlib import Path

from app.models.schemas import (
    VoiceTranscriptionRequest, 
    VoiceTranscriptionResponse, 
    TextToSpeechRequest, 
    TextToSpeechResponse,
    ErrorResponse
)
from app.services.ai.openai_service import OpenAIService, get_openai_service
from app.services.ai.voice_service import VoiceService, get_voice_service
from app.utils.helpers import sanitize_filename, is_audio_file

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/transcribe", 
             response_model=VoiceTranscriptionResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def transcribe_audio(
    file: UploadFile = File(...),
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Transcribir audio a texto usando Whisper de OpenAI.
    
    Args:
        file: Archivo de audio a transcribir (formatos: wav, mp3, m4a, etc.)
        
    Returns:
        Texto transcribido del audio
    """
    try:
        # Validar tipo de archivo
        if not is_audio_file(file.filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser de audio (wav, mp3, m4a, etc.)"
            )
        
        # Validar tamaño del archivo (max 25MB para Whisper)
        max_size = 25 * 1024 * 1024
        file.file.seek(0, 2)  # Ir al final del archivo
        file_size = file.file.tell()
        file.file.seek(0)  # Volver al inicio
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo es demasiado grande. Máximo permitido: {max_size} bytes"
            )
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Transcribir audio
            transcription = await openai_service.transcribe_audio(temp_file_path)
            
            logger.info(f"Audio transcribido - Archivo: {file.filename}, Caracteres: {len(transcription)}")
            
            return VoiceTranscriptionResponse(
                text=transcription,
                language="es",  # Podría detectarse automáticamente
                confidence=0.95  # Valor estimado
            )
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en transcripción de audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al transcribir el audio"
        )

@router.post("/speak",
             response_model=TextToSpeechResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def text_to_speech(
    request: TextToSpeechRequest,
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Convertir texto a voz usando el motor TTS.
    
    Args:
        request: Solicitud con texto a convertir a voz
        
    Returns:
        Audio generado en formato base64
    """
    try:
        # Validar texto
        if not request.text or not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El texto no puede estar vacío"
            )
        
        if len(request.text) > 5000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El texto es demasiado largo. Máximo 5000 caracteres"
            )
        
        # Guardar audio en archivo temporal
        temp_filename = f"tts_{sanitize_filename(str(hash(request.text)))}.wav"
        audio_file_path = voice_service.save_audio(request.text, temp_filename)
        
        # Leer archivo y convertirlo a base64
        with open(audio_file_path, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        
        # Estimar duración (aproximadamente 0.05 segundos por carácter)
        estimated_duration = len(request.text) * 0.05
        
        logger.info(f"TTS generado - Caracteres: {len(request.text)}, Duración estimada: {estimated_duration:.1f}s")
        
        return TextToSpeechResponse(
            audio_data=audio_data,
            duration=estimated_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en texto a voz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al generar audio"
        )

@router.post("/transcribe-and-respond")
async def transcribe_and_respond(
    file: UploadFile = File(...),
    openai_service: OpenAIService = Depends(get_openai_service),
    voice_service: VoiceService = Depends(get_voice_service)
):
    """
    Endpoint combinado: transcribir audio y obtener respuesta hablada.
    
    Args:
        file: Audio con la pregunta del usuario
        
    Returns:
        Audio con la respuesta del asistente
    """
    try:
        # Primero transcribir el audio
        transcription_response = await transcribe_audio(file, openai_service)
        user_message = transcription_response.text
        
        # Procesar con OpenAI
        response_text = await openai_service.process_command(user_message)
        
        # Convertir respuesta a audio
        tts_request = TextToSpeechRequest(text=response_text)
        tts_response = await text_to_speech(tts_request, voice_service)
        
        return {
            "transcription": user_message,
            "response_text": response_text,
            "audio_response": tts_response.audio_data,
            "duration": tts_response.duration
        }
        
    except Exception as e:
        logger.error(f"Error en transcribe-and-respond: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error procesando solicitud de voz completa"
        )