#!/usr/bin/env python3
"""
Punto de entrada principal del Asistente Virtual con FastAPI
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.endpoints import chat, voice, system, files
from app.services.ai.openai_service import OpenAIService
from app.services.ai.voice_service import VoiceService
from app.gui.modern_assistant import ModernAssistant

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
openai_service = None
voice_service = None
gui_assistant = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for the application
    """
    # Startup
    global openai_service, voice_service
    
    try:
        # Initialize services
        openai_service = OpenAIService()
        voice_service = VoiceService()
        
        # Test services
        await openai_service.health_check()
        await voice_service.health_check()
        
        logger.info("✅ Servicios inicializados correctamente")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando servicios: {e}")
        raise
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("🔴 Apagando servicios...")
    if openai_service:
        await openai_service.close()
    if voice_service:
        await voice_service.close()
    if gui_assistant:
        gui_assistant.root.quit()

# Create FastAPI application
app = FastAPI(
    title="Asistente Virtual IA",
    description="Un asistente virtual inteligente con capacidades de voz y chat",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["voice"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Página principal con documentación
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Asistente Virtual IA</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { background: #2d2d2d; padding: 20px; margin: 20px 0; border-radius: 10px; }
            a { color: #4fc3f7; text-decoration: none; }
            .endpoint { background: #333; padding: 10px; margin: 5px 0; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Asistente Virtual IA</h1>
            
            <div class="card">
                <h2>📚 Documentación de la API</h2>
                <p>Explora la API interactiva:</p>
                <ul>
                    <li><a href="/docs">📖 Documentación Swagger</a></li>
                    <li><a href="/redoc">📚 Documentación ReDoc</a></li>
                </ul>
            </div>
            
            <div class="card">
                <h2>🚀 Endpoints Principales</h2>
                
                <div class="endpoint">
                    <strong>POST /api/v1/chat/message</strong>
                    <p>Enviar mensaje al asistente</p>
                </div>
                
                <div class="endpoint">
                    <strong>POST /api/v1/voice/transcribe</strong>
                    <p>Transcribir audio a texto</p>
                </div>
                
                <div class="endpoint">
                    <strong>POST /api/v1/voice/speak</strong>
                    <p>Convertir texto a voz</p>
                </div>
                
                <div class="endpoint">
                    <strong>GET /api/v1/system/health</strong>
                    <p>Estado del sistema</p>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Interfaz Gráfica</h2>
                <p>Para usar la interfaz gráfica del asistente:</p>
                <code>python -m app.gui.modern_assistant</code>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "virtual-assistant",
        "version": "1.0.0"
    }

@app.get("/api/v1/system/info")
async def system_info():
    """
    Get system information
    """
    return {
        "service": "Virtual Assistant API",
        "version": "1.0.0",
        "features": [
            "Chat inteligente con IA",
            "Reconocimiento de voz",
            "Síntesis de voz",
            "Interfaz gráfica moderna",
            "API RESTful"
        ],
        "supported_ai_models": [
            "gpt-4",
            "gpt-3.5-turbo",
            "whisper-1"
        ]
    }

# Dependency injection functions
async def get_openai_service() -> OpenAIService:
    if openai_service is None:
        raise HTTPException(status_code=503, detail="OpenAI service not available")
    return openai_service

async def get_voice_service() -> VoiceService:
    if voice_service is None:
        raise HTTPException(status_code=503, detail="Voice service not available")
    return voice_service

def start_gui():
    """
    Start the GUI assistant (optional)
    """
    global gui_assistant
    try:
        gui_assistant = ModernAssistant()
        gui_assistant.run()
    except Exception as e:
        logger.error(f"Error starting GUI: {e}")

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )