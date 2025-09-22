"""
Dependencias para inyección en los endpoints de la API.
"""
from fastapi import Header, HTTPException, status
from typing import Optional
from app.core.config import settings

async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verificar la API key en los headers para endpoints protegidos.
    
    Args:
        x_api_key: API key proporcionada en el header
        
    Returns:
        True si la API key es válida
        
    Raises:
        HTTPException si la API key es inválida o no se proporciona
    """
    if settings.ENVIRONMENT == "development" and settings.DEBUG:
        # En desarrollo, permitir acceso sin API key
        return True
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key requerida"
        )
    
    # Aquí podrías validar contra una base de datos o lista de API keys válidas
    # Por ahora, usamos una validación simple
    valid_api_keys = ["test-api-key-123"]  # En producción, cargar desde variables de entorno
    
    if x_api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida"
        )
    
    return True