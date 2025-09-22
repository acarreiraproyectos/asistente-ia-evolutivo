import speech_recognition as sr
import pyttsx3
import asyncio
import threading
import logging
from typing import Optional
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceService:
    """Servicio para reconocimiento y síntesis de voz."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = self._setup_tts()
        self.is_listening = False
        
        # Ajustar para ruido ambiental
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
    
    def _setup_tts(self) -> pyttsx3.Engine:
        """Configurar el motor de texto a voz."""
        engine = pyttsx3.init()
        
        # Configurar propiedades de voz
        voices = engine.getProperty('voices')
        
        # Buscar voz en español
        for voice in voices:
            if 'spanish' in voice.name.lower() or 'español' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Configurar velocidad y volumen
        engine.setProperty('rate', 150)  # Velocidad de habla
        engine.setProperty('volume', 0.8)  # Volumen (0.0 a 1.0)
        
        return engine
    
    async def health_check(self) -> bool:
        """Verificar que los servicios de voz estén disponibles."""
        try:
            # Verificar micrófono
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            # Verificar TTS
            self.tts_engine.getProperty('voices')
            
            logger.info("✅ Servicios de voz configurados correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en servicios de voz: {e}")
            return False
    
    def listen(self) -> Optional[str]:
        """Escuchar audio del micrófono y convertirlo a texto."""
        try:
            logger.info("🎤 Escuchando...")
            
            with self.microphone as source:
                # Escuchar audio con timeout y ajuste de ruido
                audio = self.recognizer.listen(
                    source, 
                    timeout=settings.AUDIO_RECORD_TIMEOUT,
                    phrase_time_limit=10
                )
            
            logger.info("🔊 Audio capturado, procesando...")
            
            # Reconocer usando Google Speech Recognition
            text = self.recognizer.recognize_google(audio, language=settings.DEFAULT_LANGUAGE)
            logger.info(f"📝 Texto reconocido: {text}")
            
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("⏰ Tiempo de espera agotado, no se detectó voz")
            return None
        except sr.UnknownValueError:
            logger.warning("❌ No se pudo entender el audio")
            return None
        except sr.RequestError as e:
            logger.error(f"❌ Error en el servicio de reconocimiento: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado en listen: {e}")
            return None
    
    def speak(self, text: str):
        """Convertir texto a voz y reproducirlo."""
        try:
            logger.info(f"🗣️ Reproduciendo: {text}")
            
            # Usar un hilo para no bloquear la aplicación principal
            def _speak():
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            
            thread = threading.Thread(target=_speak)
            thread.daemon = True
            thread.start()
            
            # Esperar a que termine de hablar (aproximadamente)
            words = len(text.split())
            estimated_time = words * 0.5  # Estimación de 0.5 segundos por palabra
            
            # Retornar inmediatamente, el hilo se ejecuta en background
            return estimated_time
            
        except Exception as e:
            logger.error(f"❌ Error en speak: {e}")
            raise
    
    async def speak_async(self, text: str):
        """Versión asíncrona de speak."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.speak, text)
    
    def save_audio(self, text: str, filename: str) -> str:
        """Guardar texto como archivo de audio."""
        try:
            output_path = Path(settings.UPLOAD_FOLDER) / "audio" / f"{filename}.wav"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Usar pyttsx3 para guardar en archivo
            self.tts_engine.save_to_file(text, str(output_path))
            self.tts_engine.runAndWait()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"❌ Error guardando audio: {e}")
            raise
    
    async def close(self):
        """Limpiar recursos del servicio de voz."""
        try:
            self.tts_engine.stop()
        except Exception as e:
            logger.error(f"Error cerrando TTS engine: {e}")