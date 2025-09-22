"""
Endpoints para manejo de archivos.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
import logging
import os
from pathlib import Path

from app.models.schemas import FileUploadResponse, ErrorResponse
from app.core.config import settings
from app.utils.helpers import sanitize_filename, format_file_size, create_directory_if_not_exists

router = APIRouter()
logger = logging.getLogger(__name__)

# Crear directorio de uploads si no existe
create_directory_if_not_exists(settings.UPLOAD_FOLDER)

@router.post("/upload", 
             response_model=FileUploadResponse,
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def upload_file(file: UploadFile = File(...)):
    """
    Subir un archivo al servidor.
    
    Args:
        file: Archivo a subir
        
    Returns:
        Información del archivo subido
    """
    try:
        # Validar que se haya proporcionado un archivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se proporcionó un archivo"
            )
        
        # Validar tamaño del archivo
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El archivo excede el tamaño máximo de {format_file_size(settings.MAX_FILE_SIZE)}"
            )
        
        # Sanitizar el nombre del archivo
        safe_filename = sanitize_filename(file.filename)
        file_path = Path(settings.UPLOAD_FOLDER) / safe_filename
        
        # Verificar si el archivo ya existe y generar un nombre único si es necesario
        counter = 1
        original_stem = file_path.stem
        while file_path.exists():
            safe_filename = f"{original_stem}_{counter}{file_path.suffix}"
            file_path = Path(settings.UPLOAD_FOLDER) / safe_filename
            counter += 1
        
        # Guardar el archivo
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Archivo subido - Nombre: {safe_filename}, Tamaño: {format_file_size(file.size)}")
        
        return FileUploadResponse(
            filename=safe_filename,
            file_url=f"/uploads/{safe_filename}",  # URL relativa para acceder al archivo
            file_size=file.size,
            content_type=file.content_type or "application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error subiendo archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al subir el archivo"
        )

@router.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    """
    Subir múltiples archivos al servidor.
    
    Args:
        files: Lista de archivos a subir
        
    Returns:
        Lista de archivos subidos exitosamente
    """
    results = []
    errors = []
    
    for file in files:
        try:
            result = await upload_file(file)
            results.append(result.dict())
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "successful_uploads": results,
        "failed_uploads": errors,
        "total_files": len(files),
        "successful_count": len(results),
        "failed_count": len(errors)
    }

@router.get("/files")
async def list_uploaded_files():
    """
    Listar archivos subidos al servidor.
    
    Returns:
        Lista de archivos disponibles
    """
    upload_path = Path(settings.UPLOAD_FOLDER)
    
    if not upload_path.exists():
        return {"files": [], "total_count": 0}
    
    files = []
    for file_path in upload_path.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "filename": file_path.name,
                "size": stat.st_size,
                "size_formatted": format_file_size(stat.st_size),
                "modified_at": stat.st_mtime,
                "file_url": f"/uploads/{file_path.name}"
            })
    
    return {
        "files": sorted(files, key=lambda x: x["modified_at"], reverse=True),
        "total_count": len(files),
        "total_size": format_file_size(sum(f["size"] for f in files))
    }

@router.delete("/files/{filename}")
async def delete_file(filename: str):
    """
    Eliminar un archivo del servidor.
    
    Args:
        filename: Nombre del archivo a eliminar
    """
    try:
        # Sanitizar el nombre del archivo por seguridad
        safe_filename = sanitize_filename(filename)
        file_path = Path(settings.UPLOAD_FOLDER) / safe_filename
        
        # Verificar que el archivo existe
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo no encontrado"
            )
        
        # Verificar que es un archivo (no un directorio)
        if not file_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La ruta especificada no es un archivo"
            )
        
        # Eliminar el archivo
        file_path.unlink()
        
        logger.info(f"Archivo eliminado - Nombre: {safe_filename}")
        
        return {"message": f"Archivo {safe_filename} eliminado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando archivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al eliminar el archivo"
        )