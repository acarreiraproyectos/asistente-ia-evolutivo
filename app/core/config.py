import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Settings(BaseSettings):
    """Configuración de la aplicación a partir de variables de entorno."""
    
    # Configuración de la aplicación
    APP_NAME: str = "Virtual Assistant API"
    APP_VERSION: str = "1.0.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"  # 'development', 'staging', 'production'
    
    # Configuración del asistente
    ASSISTANT_NAME: str = "AsistenteIA"
    DEFAULT_LANGUAGE: str = "es"
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "America/Argentina/Buenos_Aires"
    MAX_TOKENS: int = 4000
    MAX_HISTORY_MESSAGES: int = 10
    REQUEST_TIMEOUT: int = 30
    
    # Seguridad
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Base de datos
    DATABASE_URL: str = "postgresql://user:password@localhost/virtual_assistant"
    DATABASE_TEST_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_URL: str = "redis://localhost:6379/1"
    
    # APIs externas (AI y Cloud)
    OPENAI_API_KEY: str = ""
    GOOGLE_AI_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    ELEVENLABS_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    
    # Servicios externos
    WEATHER_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    GEOCODING_API_KEY: str = ""
    
    # Configuración de audio
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHUNK_SIZE: int = 1024
    AUDIO_SILENCE_THRESHOLD: int = 500
    AUDIO_RECORD_TIMEOUT: int = 5
    DEFAULT_VOICE_MODEL: str = "eleven_multilingual_v1"
    DEFAULT_STT_MODEL: str = "whisper-1"
    
    # Configuración de modelos AI
    DEFAULT_AI_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    VISION_MODEL: str = "gpt-4-vision-preview"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@yourapp.com"
    EMAIL_ENABLED: bool = False
    
    # Almacenamiento
    MAX_FILE_SIZE: int = 5242880  # 5MB
    UPLOAD_FOLDER: str = "./uploads"
    STATIC_FOLDER: str = "./static"
    
    # Monitoreo
    SENTRY_DSN: str = ""
    LOG_FILE: str = "logs/app.log"
    METRICS_ENABLED: bool = True
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    API_KEY_HEADER: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()