"""
Endpoints para el chat con el asistente.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
import logging
from datetime import datetime

from app.models.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.services.ai.openai_service import OpenAIService, get_openai_service
from app.utils.helpers import generate_unique_id

router = APIRouter()
logger = logging.getLogger(__name__)

# Almacenamiento temporal en memoria (en producción usar base de datos)
conversations = {}

@router.post("/message", 
             response_model=ChatResponse, 
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def send_message(
    request: ChatRequest,
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Enviar un mensaje al asistente y obtener respuesta.
    
    Args:
        request: Solicitud de chat con el mensaje del usuario
        openai_service: Servicio de OpenAI inyectado
        
    Returns:
        Respuesta del asistente con información de la conversación
    """
    try:
        # Validar que el mensaje no esté vacío
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El mensaje no puede estar vacío"
            )
        
        # Obtener o crear la conversación
        conversation_id = request.conversation_id or generate_unique_id()
        
        if conversation_id not in conversations:
            conversations[conversation_id] = {
                "messages": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        
        conversation = conversations[conversation_id]
        
        # Agregar mensaje del usuario
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now()
        }
        conversation["messages"].append(user_message)
        
        # Limitar el historial si es necesario
        if len(conversation["messages"]) > 20:  # Mantener últimos 20 mensajes
            conversation["messages"] = conversation["messages"][-20:]
        
        # Preparar mensajes para OpenAI (formato esperado por la API)
        openai_messages = []
        
        # Agregar mensaje del sistema para definir el comportamiento del asistente
        system_message = {
            "role": "system",
            "content": f"""Eres un asistente virtual útil y amigable llamado {openai_service.assistant_name}.
            Responde en español de manera clara y concisa.
            Sé profesional pero accesible en tus respuestas.
            Si no sabes algo, admítelo honestamente."""
        }
        openai_messages.append(system_message)
        
        # Agregar historial de conversación
        for msg in conversation["messages"][-10:]:  # Últimos 10 mensajes para contexto
            openai_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Obtener respuesta del asistente
        response_text = await openai_service.chat_completion(openai_messages)
        
        # Agregar respuesta del asistente a la conversación
        assistant_message = {
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now()
        }
        conversation["messages"].append(assistant_message)
        conversation["updated_at"] = datetime.now()
        
        logger.info(f"Chat procesado - Conversación: {conversation_id}, Mensajes: {len(conversation['messages'])}")
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            timestamp=datetime.now(),
            tokens_used=None  # Podría obtenerse de la respuesta de OpenAI
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en endpoint de chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al procesar el mensaje"
        )

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Obtener el historial completo de una conversación.
    
    Args:
        conversation_id: ID de la conversación a recuperar
        
    Returns:
        Historial completo de la conversación
    """
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]["messages"],
        "created_at": conversations[conversation_id]["created_at"],
        "updated_at": conversations[conversation_id]["updated_at"],
        "message_count": len(conversations[conversation_id]["messages"])
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Eliminar una conversación específica.
    
    Args:
        conversation_id: ID de la conversación a eliminar
    """
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversación {conversation_id} eliminada correctamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversación no encontrada"
        )

@router.get("/conversations")
async def list_conversations():
    """
    Listar todas las conversaciones activas.
    
    Returns:
        Lista de conversaciones con información básica
    """
    result = []
    for conv_id, conv_data in conversations.items():
        result.append({
            "conversation_id": conv_id,
            "created_at": conv_data["created_at"],
            "updated_at": conv_data["updated_at"],
            "message_count": len(conv_data["messages"]),
            "last_message": conv_data["messages"][-1]["content"][:100] + "..." if conv_data["messages"] else ""
        })
    
    return {
        "conversations": result,
        "total_count": len(result)
    }