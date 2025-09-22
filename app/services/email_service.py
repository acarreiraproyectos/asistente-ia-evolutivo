"""
Servicio para envío de emails.
"""
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para enviar correos electrónicos."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.email_from = settings.EMAIL_FROM
        self.enabled = settings.EMAIL_ENABLED
    
    def send_email(self, to_emails: List[str], subject: str, body: str, is_html: bool = False) -> bool:
        """
        Enviar un correo electrónico.
        
        Args:
            to_emails: Lista de direcciones de correo destinatario
            subject: Asunto del correo
            body: Cuerpo del correo
            is_html: Si el cuerpo es HTML (True) o texto plano (False)
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.enabled:
            logger.warning("El servicio de email está deshabilitado")
            return False
        
        try:
            # Crear el mensaje
            msg = MimeMultipart()
            msg['From'] = self.email_from
            msg['To'] = ", ".join(to_emails)
            msg['Subject'] = subject
            
            # Adjuntar el cuerpo del mensaje
            if is_html:
                msg.attach(MimeText(body, 'html'))
            else:
                msg.attach(MimeText(body, 'plain'))
            
            # Conectar y enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Seguridad TLS
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email enviado a {to_emails}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def send_notification(self, to_emails: List[str], title: str, message: str) -> bool:
        """
        Enviar una notificación por email.
        
        Args:
            to_emails: Lista de direcciones de correo destinatario
            title: Título de la notificación
            message: Mensaje de la notificación
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        body = f"""
        <html>
          <body>
            <h2>{title}</h2>
            <p>{message}</p>
            <hr>
            <p><small>Notificación enviada por {settings.APP_NAME}</small></p>
          </body>
        </html>
        """
        
        return self.send_email(to_emails, title, body, is_html=True)
    
    def send_error_notification(self, to_emails: List[str], error_message: str, context: Optional[str] = None) -> bool:
        """
        Enviar una notificación de error.
        
        Args:
            to_emails: Lista de direcciones de correo destinatario
            error_message: Mensaje de error
            context: Contexto adicional del error
            
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        subject = f"Error en {settings.APP_NAME}"
        message = f"Se ha producido un error: {error_message}"
        
        if context:
            message += f"\n\nContexto: {context}"
        
        return self.send_notification(to_emails, subject, message)

# Instancia global del servicio de email
email_service = EmailService()