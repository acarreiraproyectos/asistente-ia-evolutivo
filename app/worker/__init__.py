"""
Módulo de workers para tareas en segundo plano.
"""

from .celery import celery_app

__all__ = ['celery_app']