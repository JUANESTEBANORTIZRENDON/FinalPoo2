"""
Vista de autenticación para acceso al Django Admin desde el dashboard del holding.
Requiere contraseña adicional de desarrollador para mayor seguridad.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseForbidden
import hashlib
import os

# Contraseña por defecto (puede cambiarse por comando)
DEFAULT_DEV_PASSWORD = "contraseña"

def get_dev_password():
    """
    Obtiene la contraseña de desarrollador desde variable de entorno o usa la por defecto.
    """
    return os.environ.get('DJANGO_DEV_PASSWORD', DEFAULT_DEV_PASSWORD)

def hash_password(password):
    """
    Genera hash SHA256 de la contraseña para comparación segura.
    """
    return hashlib.sha256(password.encode()).hexdigest()

@login_required
@require_http_methods(["GET", "POST"])
def dev_auth_required(request):
    """
    Vista que solicita contraseña de desarrollador antes de acceder al Django Admin.
    """
    # Verificar que el usuario sea administrador del holding
    if not _es_admin_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder al panel de desarrollador.')
        return redirect('empresas:admin_dashboard')
    
    if request.method == 'POST':
        password = request.POST.get('dev_password', '')
        correct_password = get_dev_password()
        
        if password == correct_password:
            # Guardar en sesión que ya se autenticó como desarrollador
            request.session['dev_authenticated'] = True
            request.session['dev_auth_time'] = request.session.get('_session_key', '')
            
            # Redirigir al Django Admin
            return redirect('/admin/')
        else:
            messages.error(request, 'Contraseña de desarrollador incorrecta.')
    
    return render(request, 'empresas/admin/dev_auth.html')

def _es_admin_holding(user):
    """Verifica si el usuario es administrador del holding"""
    return user.is_superuser or user.perfilempresa_set.filter(rol='admin', activo=True).exists()

def _es_ruta_admin_protegida(path):
    """Verifica si la ruta requiere autenticación de desarrollador"""
    return (path.startswith('/admin/') and 
            not path.startswith('/admin/login/') and 
            not path.startswith('/admin/logout/'))

def _verificar_autenticacion_basica(request):
    """Verifica autenticación básica de Django"""
    if not request.user.is_authenticated:
        return False, redirect('/admin/login/')
    return True, None

def _verificar_permisos_admin(request):
    """Verifica permisos de administrador del holding"""
    if not _es_admin_holding(request.user):
        return False, HttpResponseForbidden("Acceso denegado: Se requiere ser administrador del holding.")
    return True, None

def _verificar_auth_desarrollador(request):
    """Verifica autenticación de desarrollador (excepto superusuarios)"""
    if not request.user.is_superuser:
        dev_authenticated = request.session.get('dev_authenticated', False)
        if not dev_authenticated:
            return False, redirect('empresas:dev_auth_required')
    return True, None

def dev_auth_middleware(get_response):
    """
    Middleware para verificar autenticación de desarrollador en rutas /admin/
    """
    def middleware(request):
        # Solo aplicar a rutas /admin/ protegidas
        if not _es_ruta_admin_protegida(request.path):
            return get_response(request)
        
        # Verificar autenticación básica
        ok, response = _verificar_autenticacion_basica(request)
        if not ok:
            return response
        
        # Verificar permisos de administrador
        ok, response = _verificar_permisos_admin(request)
        if not ok:
            return response
        
        # Verificar autenticación de desarrollador
        ok, response = _verificar_auth_desarrollador(request)
        if not ok:
            return response
        
        return get_response(request)
    
    return middleware
