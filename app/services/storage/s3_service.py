"""
Servicio para almacenamiento en AWS S3.
"""
import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3StorageService:
    """Servicio para manejar almacenamiento en AWS S3."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.AWS_S3_BUCKET
    
    def save_file(self, file_data: BinaryIO, filename: str, subdirectory: Optional[str] = None) -> str:
        """
        Guardar un archivo en S3.
        
        Args:
            file_data: Datos del archivo (objeto de archivo o BytesIO)
            filename: Nombre del archivo
            subdirectory: Subdirectorio donde guardar el archivo
            
        Returns:
            Clave del objeto en S3
        """
        try:
            # Construir la clave (key) del objeto
            if subdirectory:
                key = f"{subdirectory}/{filename}"
            else:
                key = filename
            
            # Subir el archivo a S3
            self.s3_client.upload_fileobj(file_data, self.bucket_name, key)
            
            logger.info(f"Archivo guardado en S3: {key}")
            return key
            
        except ClientError as e:
            logger.error(f"Error guardando archivo en S3: {e}")
            raise
    
    def get_file_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Obtener una URL firmada para acceder a un archivo en S3.
        
        Args:
            key: Clave del objeto en S3
            expires_in: Tiempo de expiración de la URL en segundos (por defecto 1 hora)
            
        Returns:
            URL firmada para acceder al archivo
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Error generando URL para {key}: {e}")
            raise
    
    def delete_file(self, key: str) -> bool:
        """
        Eliminar un archivo de S3.
        
        Args:
            key: Clave del objeto en S3
            
        Returns:
            True si se eliminó correctamente, False si no existía
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Archivo eliminado de S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error eliminando archivo de S3: {e}")
            return False
    
    def file_exists(self, key: str) -> bool:
        """
        Verificar si un archivo existe en S3.
        
        Args:
            key: Clave del objeto en S3
            
        Returns:
            True si existe, False en caso contrario
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

# Instancia global del servicio de S3 (solo si las credenciales están configuradas)
s3_storage = None
if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.AWS_S3_BUCKET:
    s3_storage = S3StorageService()