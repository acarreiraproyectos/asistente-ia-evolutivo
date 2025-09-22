"""
Esquemas Pydantic para la aplicación.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Esquema para un mensaje de chat."""
    role: MessageRole
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    """Esquema para una solicitud de chat."""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Esquema para una respuesta de chat."""
    response: str
    conversation_id: Optional[str] = None
    timestamp: datetime
    tokens_used: Optional[int] = None

class VoiceTranscriptionRequest(BaseModel):
    """Esquema para una solicitud de transcripción de voz."""
    audio_data: Optional[str] = None  # Base64 encoded audio
    audio_url: Optional[str] = None   # URL to audio file
    language: str = "es"

class VoiceTranscriptionResponse(BaseModel):
    """Esquema para una respuesta de transcripción de voz."""
    text: str
    confidence: Optional[float] = None
    language: str

class TextToSpeechRequest(BaseModel):
    """Esquema para una solicitud de texto a voz."""
    text: str = Field(..., min_length=1, max_length=5000)
    voice_model: Optional[str] = None
    speed: Optional[float] = Field(1.0, ge=0.5, le=2.0)

class TextToSpeechResponse(BaseModel):
    """Esquema para una respuesta de texto a voz."""
    audio_url: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio
    duration: Optional[float] = None

class Conversation(BaseModel):
    """Esquema para una conversación completa."""
    id: Optional[str] = None
    title: str
    messages: List[ChatMessage] = []
    created_at: datetime
    updated_at: datetime

class User(BaseModel):
    """Esquema para un usuario."""
    id: Optional[str] = None
    username: str
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

class UserCreate(BaseModel):
    """Esquema para crear un usuario."""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[str] = None
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    """Esquema para login de usuario."""
    username: str
    password: str

class Token(BaseModel):
    """Esquema para token de acceso."""
    access_token: str
    token_type: str = "bearer"

class HealthCheck(BaseModel):
    """Esquema para verificación de salud."""
    status: str
    service: str
    version: str
    timestamp: datetime

class ErrorResponse(BaseModel):
    """Esquema para respuestas de error."""
    error: str
    details: Optional[str] = None
    code: Optional[int] = None

class FileUploadResponse(BaseModel):
    """Esquema para respuesta de subida de archivo."""
    filename: str
    file_url: Optional[str] = None
    file_size: int
    content_type: str

class AnalysisRequest(BaseModel):
    """Esquema para solicitud de análisis."""
    text: Optional[str] = None
    file_url: Optional[str] = None
    analysis_type: str  # "sentiment", "summary", "keywords", etc.

class AnalysisResponse(BaseModel):
    """Esquema para respuesta de análisis."""
    analysis_type: str
    results: Dict[str, Any]
    confidence: Optional[float] = None