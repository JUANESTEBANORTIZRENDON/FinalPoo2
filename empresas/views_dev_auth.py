"""
Vista de autenticación para acceso al Django Admin desde el dashboard del holding.
Requiere contraseña adicional de desarrollador para mayor seguridad.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
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
def dev_auth_required(request):
    """
    Vista que solicita contraseña de desarrollador antes de acceder al Django Admin.
    """
    # Verificar que el usuario sea administrador del holding
    if not (request.user.is_superuser or 
            request.user.perfilempresa_set.filter(rol='admin', activo=True).exists()):
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

def dev_auth_middleware(get_response):
    """
    Middleware para verificar autenticación de desarrollador en rutas /admin/
    """
    def middleware(request):
        # Solo aplicar a rutas /admin/ (excepto login y logout)
        if (request.path.startswith('/admin/') and 
            not request.path.startswith('/admin/login/') and 
            not request.path.startswith('/admin/logout/')):
            
            # Verificar que esté autenticado en Django
            if not request.user.is_authenticated:
                return redirect('/admin/login/')
            
            # Verificar que tenga permisos de administrador del holding
            if not (request.user.is_superuser or 
                    request.user.perfilempresa_set.filter(rol='admin', activo=True).exists()):
                return HttpResponseForbidden("Acceso denegado: Se requiere ser administrador del holding.")
            
            # Verificar autenticación de desarrollador (excepto para superusuarios)
            if not request.user.is_superuser:
                dev_authenticated = request.session.get('dev_authenticated', False)
                if not dev_authenticated:
                    return redirect('empresas:dev_auth_required')
        
        response = get_response(request)
        return response
    
    return middleware
