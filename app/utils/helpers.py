"""
Utilidades generales para la aplicación.
"""
import base64
import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_unique_id() -> str:
    """Generar un ID único."""
    return str(uuid.uuid4())

def format_timestamp(timestamp: datetime) -> str:
    """Formatear timestamp para mostrar."""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def safe_get(dictionary: Dict, keys: List[str], default: Any = None) -> Any:
    """Obtener valor de diccionario de forma segura."""
    try:
        for key in keys:
            dictionary = dictionary[key]
        return dictionary
    except (KeyError, TypeError):
        return default

def validate_email(email: str) -> bool:
    """Validar formato de email."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncar texto y agregar ellipsis si es necesario."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def format_file_size(size_bytes: int) -> str:
    """Formatear tamaño de archivo en formato legible."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names)-1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def create_directory_if_not_exists(path: str) -> bool:
    """Crear directorio si no existe."""
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creando directorio {path}: {e}")
        return False

def encode_base64(data: str) -> str:
    """Codificar string a base64."""
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def decode_base64(data: str) -> str:
    """Decodificar string desde base64."""
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')

def calculate_md5(data: str) -> str:
    """Calcular hash MD5 de un string."""
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo para evitar problemas de seguridad."""
    # Remover caracteres peligrosos
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limitar longitud
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1)
        filename = name[:255-len(ext)-1] + '.' + ext
    
    return filename

def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """Dividir texto en chunks del tamaño especificado."""
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        if len(' '.join(current_chunk + [word])) <= chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def get_file_extension(filename: str) -> str:
    """Obtener extensión de archivo."""
    return Path(filename).suffix.lower()

def is_audio_file(filename: str) -> bool:
    """Verificar si el archivo es de audio."""
    audio_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac'}
    return get_file_extension(filename) in audio_extensions

def is_text_file(filename: str) -> bool:
    """Verificar si el archivo es de texto."""
    text_extensions = {'.txt', '.md', '.csv', '.json', '.xml', '.html'}
    return get_file_extension(filename) in text_extensions

def format_duration(seconds: int) -> str:
    """Formatear duración en segundos a formato MM:SS."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

class RateLimiter:
    """Simple rate limiter para controlar frecuencia de solicitudes."""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def is_allowed(self) -> bool:
        """Verificar si la solicitud está permitida."""
        now = datetime.now()
        
        # Remover solicitudes fuera de la ventana de tiempo
        self.requests = [req for req in self.requests 
                        if (now - req).total_seconds() <= self.time_window]
        
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        
        return False