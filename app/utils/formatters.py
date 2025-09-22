"""
Formateadores de respuesta para la aplicación.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
import json

def format_datetime(dt: datetime, format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    Formatear datetime a string.
    
    Args:
        dt: Objeto datetime
        format: Formato deseado
        
    Returns:
        String formateado
    """
    if not dt:
        return ""
    return dt.strftime(format)

def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Formatear cantidad como moneda.
    
    Args:
        amount: Cantidad a formatear
        currency: Código de moneda (USD, EUR, etc.)
        
    Returns:
        String formateado como moneda
    """
    if currency == 'USD':
        return f"${amount:,.2f}"
    elif currency == 'EUR':
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Formatear valor como porcentaje.
    
    Args:
        value: Valor a formatear (ej: 0.95 para 95%)
        decimals: Número de decimales
        
    Returns:
        String formateado como porcentaje
    """
    return f"{value * 100:.{decimals}f}%"

def format_file_size(size_bytes: int) -> str:
    """
    Formatear tamaño de archivo en formato legible.
    
    Args:
        size_bytes: Tamaño en bytes
        
    Returns:
        String formateado (ej: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

def format_duration(seconds: int) -> str:
    """
    Formatear duración en segundos a formato legible.
    
    Args:
        seconds: Duración en segundos
        
    Returns:
        String formateado (ej: "01:30:25")
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_phone_number(phone: str) -> str:
    """
    Formatear número de teléfono a formato internacional estándar.
    
    Args:
        phone: Número de teléfono a formatear
        
    Returns:
        Número formateado (ej: "+34 123 456 789")
    """
    # Limpiar el número
    cleaned = ''.join(filter(str.isdigit, phone))
    
    if cleaned.startswith('0'):
        cleaned = '+34' + cleaned[1:]  # Asumir España por defecto
    
    if not cleaned.startswith('+'):
        cleaned = '+' + cleaned
    
    # Formatear con espacios cada 3 dígitos
    formatted = cleaned[:3]  # Código de país
    remaining = cleaned[3:]
    
    for i in range(0, len(remaining), 3):
        formatted += ' ' + remaining[i:i+3]
    
    return formatted.strip()

def format_json(data: Any, indent: int = 2) -> str:
    """
    Formatear datos como JSON legible.
    
    Args:
        data: Datos a formatear
        indent: Indentación del JSON
        
    Returns:
        String JSON formateado
    """
    return json.dumps(data, indent=indent, ensure_ascii=False, default=str)

def format_list(items: List[Any], separator: str = ', ', max_items: Optional[int] = None) -> str:
    """
    Formatear lista como string.
    
    Args:
        items: Lista de items
        separator: Separador entre items
        max_items: Número máximo de items a mostrar
        
    Returns:
        String formateado
    """
    if not items:
        return ""
    
    if max_items and len(items) > max_items:
        displayed = items[:max_items]
        return separator.join(str(item) for item in displayed) + f", ... (+{len(items) - max_items})"
    else:
        return separator.join(str(item) for item in items)

def format_error_message(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """
    Formatear mensaje de error para respuesta API.
    
    Args:
        error: Excepción a formatear
        include_traceback: Incluir traceback (solo en desarrollo)
        
    Returns:
        Diccionario con información del error
    """
    result = {
        'error_type': error.__class__.__name__,
        'error_message': str(error)
    }
    
    if include_traceback:
        import traceback
        result['traceback'] = traceback.format_exc()
    
    return result

def format_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Formatear respuesta de éxito estándar.
    
    Args:
        data: Datos a incluir en la respuesta
        message: Mensaje opcional
        
    Returns:
        Diccionario con formato de respuesta exitosa
    """
    response = {
        'success': True,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    
    if message:
        response['message'] = message
    
    return response

def format_error_response(error: str, details: Optional[str] = None, code: Optional[int] = None) -> Dict[str, Any]:
    """
    Formatear respuesta de error estándar.
    
    Args:
        error: Mensaje de error
        details: Detalles adicionales del error
        code: Código de error opcional
        
    Returns:
        Diccionario con formato de respuesta de error
    """
    response = {
        'success': False,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }
    
    if details:
        response['details'] = details
    
    if code:
        response['code'] = code
    
    return response