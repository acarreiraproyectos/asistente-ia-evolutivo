"""
Validadores de datos para la aplicación.
"""
import re
from typing import Any, Optional
from datetime import datetime
from email.utils import parseaddr

def validate_email(email: str) -> bool:
    """
    Validar formato de email.
    
    Args:
        email: Dirección de email a validar
        
    Returns:
        True si el email es válido, False en caso contrario
    """
    if not email or not isinstance(email, str):
        return False
    
    # Usar parseaddr para validar el formato
    parsed = parseaddr(email)
    if parsed[1] == '':
        return False
    
    # Verificar que tenga un formato básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """
    Validar número de teléfono (formato internacional: +34 123 456 789).
    
    Args:
        phone: Número de teléfono a validar
        
    Returns:
        True si el teléfono es válido, False en caso contrario
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Patrón para números internacionales
    pattern = r'^\+?[1-9]\d{1,14}$'
    # Limpiar espacios y guiones
    cleaned_phone = re.sub(r'[\s\-]', '', phone)
    return bool(re.match(pattern, cleaned_phone))

def validate_date(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """
    Validar fecha en formato específico.
    
    Args:
        date_string: String con la fecha
        format: Formato esperado (por defecto YYYY-MM-DD)
        
    Returns:
        True si la fecha es válida, False en caso contrario
    """
    try:
        datetime.strptime(date_string, format)
        return True
    except (ValueError, TypeError):
        return False

def validate_url(url: str) -> bool:
    """
    Validar URL.
    
    Args:
        url: URL a validar
        
    Returns:
        True si la URL es válida, False en caso contrario
    """
    if not url or not isinstance(url, str):
        return False
    
    pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&]*$'
    return bool(re.match(pattern, url))

def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validar extensión de archivo.
    
    Args:
        filename: Nombre del archivo
        allowed_extensions: Conjunto de extensiones permitidas
        
    Returns:
        True si la extensión es válida, False en caso contrario
    """
    if not filename:
        return False
    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validar tamaño de archivo.
    
    Args:
        file_size: Tamaño del archivo en bytes
        max_size: Tamaño máximo permitido en bytes
        
    Returns:
        True si el tamaño es válido, False en caso contrario
    """
    return file_size <= max_size

def validate_password_strength(password: str) -> dict:
    """
    Validar fortaleza de contraseña.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Diccionario con resultados de la validación
    """
    results = {
        'is_valid': True,
        'issues': []
    }
    
    if len(password) < 8:
        results['is_valid'] = False
        results['issues'].append('La contraseña debe tener al menos 8 caracteres')
    
    if not re.search(r'[A-Z]', password):
        results['is_valid'] = False
        results['issues'].append('La contraseña debe contener al menos una mayúscula')
    
    if not re.search(r'[a-z]', password):
        results['is_valid'] = False
        results['issues'].append('La contraseña debe contener al menos una minúscula')
    
    if not re.search(r'[0-9]', password):
        results['is_valid'] = False
        results['issues'].append('La contraseña debe contener al menos un número')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        results['is_valid'] = False
        results['issues'].append('La contraseña debe contener al menos un carácter especial')
    
    return results

def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitizar entrada de texto para prevenir ataques XSS básicos.
    
    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima permitida
        
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
    
    # Eliminar etiquetas HTML/XML
    cleaned = re.sub(r'<[^>]*>', '', text)
    
    # Escapar caracteres especiales
    cleaned = cleaned.replace('&', '&amp;')
    cleaned = cleaned.replace('<', '&lt;')
    cleaned = cleaned.replace('>', '&gt;')
    cleaned = cleaned.replace('"', '&quot;')
    cleaned = cleaned.replace("'", '&#x27;')
    
    # Limitar longitud si se especifica
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned