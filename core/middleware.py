"""
Middleware personalizado para el proyecto S_CONTABLE
"""
from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)


class DevCSRFMiddleware(MiddlewareMixin):
    """
    Middleware para facilitar el desarrollo con CSRF
    Solo se activa en modo DEBUG
    """
    
    def process_request(self, request):
        if settings.DEBUG:
            # Agregar headers útiles para debugging
            if hasattr(request, 'META'):
                origin = request.META.get('HTTP_ORIGIN', 'No Origin')
                referer = request.META.get('HTTP_REFERER', 'No Referer')
                
                # Log para debugging
                if request.method == 'POST':
                    logger.debug(f"POST Request - Origin: {origin}, Referer: {referer}")
        
        return None
    
    def process_response(self, request, response):
        if settings.DEBUG:
            # Agregar headers CORS adicionales para desarrollo
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, Authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response


class CustomCsrfViewMiddleware(CsrfViewMiddleware):
    """
    Middleware CSRF personalizado para mejor manejo en desarrollo
    """
    
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG:
            # En desarrollo, ser más permisivo con CSRF
            # Pero mantener la seguridad básica
            
            # Verificar si es una vista que necesita CSRF
            if getattr(callback, 'csrf_exempt', False):
                return None
            
            # Para formularios HTML, asegurar que el token esté presente
            if request.method == 'POST' and request.content_type == 'application/x-www-form-urlencoded':
                csrf_token = request.POST.get('csrfmiddlewaretoken')
                if not csrf_token:
                    logger.warning(f"CSRF token missing in POST to {request.path}")
        
        # Llamar al middleware original
        return super().process_view(request, callback, callback_args, callback_kwargs)
