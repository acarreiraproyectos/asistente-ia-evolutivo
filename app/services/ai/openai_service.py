import openai
from openai import AsyncOpenAI
from typing import Optional, Dict, Any
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Servicio para interactuar con la API de OpenAI."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = settings.DEFAULT_AI_MODEL
        self.max_tokens = settings.MAX_TOKENS
    
    async def health_check(self) -> bool:
        """Verificar que el servicio de OpenAI esté disponible."""
        try:
            await self.client.models.list()
            logger.info("✅ Servicio OpenAI conectado correctamente")
            return True
        except Exception as e:
            logger.error(f"❌ Error conectando con OpenAI: {e}")
            return False
    
    async def chat_completion(self, messages: list, model: Optional[str] = None) -> str:
        """Obtener completación de chat desde OpenAI."""
        try:
            model = model or self.default_model
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error en chat_completion: {e}")
            raise
    
    async def process_command(self, command: str, context: Optional[Dict] = None) -> str:
        """Procesar un comando del usuario con contexto."""
        system_message = {
            "role": "system",
            "content": f"""Eres un asistente virtual útil y amigable llamado {settings.ASSISTANT_NAME}.
            Responde en el idioma: {settings.DEFAULT_LANGUAGE}.
            Sé conciso pero amable en tus respuestas."""
        }
        
        user_message = {
            "role": "user",
            "content": command
        }
        
        messages = [system_message, user_message]
        
        # Agregar contexto si está disponible
        if context:
            context_message = {
                "role": "system",
                "content": f"Contexto adicional: {context}"
            }
            messages.insert(1, context_message)
        
        return await self.chat_completion(messages)
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribir audio a texto usando Whisper."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcription = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=settings.DEFAULT_LANGUAGE
                )
            return transcription.text
        except Exception as e:
            logger.error(f"Error transcribiendo audio: {e}")
            raise
    
    async def close(self):
        """Cerrar el cliente de OpenAI."""
        await self.client.close()