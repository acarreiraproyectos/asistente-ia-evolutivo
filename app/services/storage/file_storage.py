"""
Servicio para almacenamiento local de archivos.
"""
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class FileStorageService:
    """Servicio para manejar almacenamiento local de archivos."""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or settings.UPLOAD_FOLDER)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save_file(self, file_data: BinaryIO, filename: str, subdirectory: Optional[str] = None) -> str:
        """
        Guardar un archivo en el almacenamiento local.
        
        Args:
            file_data: Datos del archivo (objeto de archivo o BytesIO)
            filename: Nombre del archivo
            subdirectory: Subdirectorio donde guardar el archivo
            
        Returns:
            Ruta relativa del archivo guardado
        """
        try:
            # Crear la ruta completa
            if subdirectory:
                file_path = self.base_path / subdirectory / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                file_path = self.base_path / filename
            
            # Guardar el archivo
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file_data, f)
            
            logger.info(f"Archivo guardado: {file_path}")
            return str(file_path.relative_to(self.base_path))
            
        except Exception as e:
            logger.error(f"Error guardando archivo {filename}: {e}")
            raise
    
    def get_file(self, filepath: str) -> Path:
        """
        Obtener la ruta completa de un archivo.
        
        Args:
            filepath: Ruta relativa del archivo
            
        Returns:
            Ruta completa del archivo
            
        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        full_path = self.base_path / filepath
        
        if not full_path.exists():
            raise FileNotFoundError(f"El archivo {filepath} no existe")
        
        return full_path
    
    def delete_file(self, filepath: str) -> bool:
        """
        Eliminar un archivo.
        
        Args:
            filepath: Ruta relativa del archivo
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        full_path = self.base_path / filepath
        
        if full_path.exists():
            full_path.unlink()
            logger.info(f"Archivo eliminado: {filepath}")
            return True
        
        return False
    
    def list_files(self, subdirectory: Optional[str] = None) -> list:
        """
        Listar archivos en un directorio.
        
        Args:
            subdirectory: Subdirectorio a listar
            
        Returns:
            Lista de nombres de archivo
        """
        if subdirectory:
            directory = self.base_path / subdirectory
        else:
            directory = self.base_path
        
        if not directory.exists():
            return []
        
        return [f.name for f in directory.iterdir() if f.is_file()]
    
    def get_file_url(self, filepath: str) -> str:
        """
        Obtener la URL para acceder a un archivo.
        
        Args:
            filepath: Ruta relativa del archivo
            
        Returns:
            URL relativa del archivo
        """
        return f"/uploads/{filepath}"

# Instancia global del servicio de almacenamiento de archivos
file_storage = FileStorageService()