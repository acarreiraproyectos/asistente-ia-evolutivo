"""
Módulo de endpoints de la API.
"""

from .chat import router as chat_router
from .voice import router as voice_router
from .system import router as system_router
from .files import router as files_router

__all__ = ['chat_router', 'voice_router', 'system_router', 'files_router']