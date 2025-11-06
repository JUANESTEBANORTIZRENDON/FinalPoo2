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
import secrets
import string

def generate_secure_password(length=32):
    """
    Genera una contraseña aleatoria segura.
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_dev_password():
    """
    Obtiene la contraseña de desarrollador desde variable de entorno.
    Si no está configurada, genera una aleatoria y muestra advertencia.
    
    IMPORTANTE: Configura DJANGO_DEV_PASSWORD en el archivo .env
    """
    password = os.environ.get('DJANGO_DEV_PASSWORD')
    
    if not password:
        # Generar contraseña aleatoria temporal
        password = generate_secure_password()
        print("=" * 70)
        print("⚠️  ADVERTENCIA: DJANGO_DEV_PASSWORD no está configurada")
        print("=" * 70)
        print(f"Contraseña temporal generada: {password}")
        print("\nPara producción, configura en tu archivo .env:")
        print(f"DJANGO_DEV_PASSWORD={password}")
        print("=" * 70)
    
    return password

def hash_password(password):
    """
    Genera hash SHA256 de la contraseña para comparación segura.
    """
    return hashlib.sha256(password.encode()).hexdigest()

@login_required
@require_http_methods(['GET', 'POST'])
# ✅ SEGURIDAD REVISADA: Patrón estándar de formulario Django
# - GET: Muestra formulario (solo lectura, operación segura)
# - POST: Procesa datos (protegido por CSRF middleware de Django)
# - Token CSRF verificado automáticamente por CsrfViewMiddleware
# - Documentación: Ver SECURITY_HTTP_METHODS_REVIEWED.md sección 1
def dev_auth_required(request):
    """
    Vista que solicita contraseña de desarrollador antes de acceder al Django Admin.
    
    Seguridad:
    - Requiere autenticación previa (@login_required)
    - Verifica permisos de administrador del holding
    - Contraseña adicional de desarrollador
    - Protección CSRF activa en peticiones POST
    - GET no modifica estado (principio de métodos seguros HTTP)
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
