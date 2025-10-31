"""
Middleware para gestionar la empresa activa en el sistema multi-tenant.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Empresa, PerfilEmpresa, EmpresaActiva

# Constante para evitar duplicación del literal 'empresas:cambiar_empresa'
CAMBIAR_EMPRESA_URL = 'empresas:cambiar_empresa'


class EmpresaActivaMiddleware:
    """
    Middleware que gestiona la empresa activa para cada usuario.
    
    - Verifica que el usuario tenga acceso a empresas
    - Establece la empresa activa en la sesión
    - Filtra los datos por empresa activa
    - Redirige a selección de empresa si es necesario
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # URLs que no requieren empresa activa
        self.exempt_urls = [
            '/accounts/login/',
            '/accounts/logout/',
            '/accounts/register/',
            '/api/',
            '/admin/',
            '/empresas/cambiar-empresa/',
            '/empresas/seleccionar/',
            '/empresas/crear/',
            '/empresas/',
        ]
    
    def __call__(self, request):
        # Procesar la request antes de la vista
        self.process_request(request)
        
        # Obtener la respuesta de la vista
        response = self.get_response(request)
        
        return response
    
    def process_request(self, request):
        """
        Procesa la request para establecer la empresa activa.
        """
        # Solo procesar para usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Verificar si la URL está exenta
        if self.is_exempt_url(request.path):
            return None
        
        # Verificar si el usuario es superusuario (acceso completo)
        if request.user.is_superuser:
            # Los superusuarios pueden acceder sin restricciones
            return None
        
        # Obtener empresas del usuario
        perfiles_empresa = PerfilEmpresa.objects.filter(
            usuario=request.user,
            activo=True
        ).select_related('empresa')
        
        if not perfiles_empresa.exists():
            # El usuario no tiene acceso a ninguna empresa
            messages.error(
                request,
                'No tienes acceso a ninguna empresa. Contacta al administrador.'
            )
            return redirect('accounts:dashboard')
        
        # Obtener empresa activa
        empresa_activa = self.get_empresa_activa(request, perfiles_empresa)
        
        if not empresa_activa:
            # Redirigir a selección de empresa
            return redirect(CAMBIAR_EMPRESA_URL)
        
        # Obtener perfil del usuario en la empresa activa
        try:
            perfil_empresa = perfiles_empresa.get(empresa=empresa_activa)
            
            # Actualizar la sesión con la información más reciente
            request.session['empresa_activa_id'] = empresa_activa.id
            request.session['empresa_activa_nombre'] = empresa_activa.razon_social
            request.session['rol_empresa'] = perfil_empresa.rol
            
            # Establecer atributos en el request para acceso fácil
            request.empresa_activa = empresa_activa
            request.perfil_empresa = perfil_empresa
            request.rol_empresa = perfil_empresa.rol
            
            # Redirigir al dashboard específico del rol si está en la raíz
            if request.path == '/' or request.path == '/accounts/dashboard/':
                return self.redirect_to_role_dashboard(perfil_empresa.rol)
                
        except PerfilEmpresa.DoesNotExist:
            # El usuario no tiene acceso a la empresa activa
            messages.error(
                request,
                'No tienes acceso a la empresa seleccionada.'
            )
            return redirect(CAMBIAR_EMPRESA_URL)
        
        return None
    
    def get_empresa_activa(self, request, perfiles_empresa):
        """
        Obtiene la empresa activa para el usuario.
        
        Prioridad:
        1. Empresa en la sesión
        2. Empresa activa guardada en BD
        3. Primera empresa disponible
        """
        # 1. Verificar empresa en sesión
        empresa_id_sesion = request.session.get('empresa_activa_id')
        if empresa_id_sesion:
            try:
                empresa = Empresa.objects.get(
                    id=empresa_id_sesion,
                    activa=True
                )
                # Verificar que el usuario tenga acceso
                if perfiles_empresa.filter(empresa=empresa).exists():
                    return empresa
            except Empresa.DoesNotExist:
                pass
        
        # 2. Verificar empresa activa en BD
        try:
            empresa_activa_obj = EmpresaActiva.objects.get(usuario=request.user)
            empresa = empresa_activa_obj.empresa
            
            # Verificar que siga siendo válida
            if (empresa.activa and 
                perfiles_empresa.filter(empresa=empresa).exists()):
                
                # Sincronizar con sesión
                request.session['empresa_activa_id'] = empresa.id
                return empresa
            else:
                # Eliminar registro obsoleto
                empresa_activa_obj.delete()
        except EmpresaActiva.DoesNotExist:
            pass
        
        # 3. Usar primera empresa disponible
        primer_perfil = perfiles_empresa.first()
        if primer_perfil:
            empresa = primer_perfil.empresa
            
            # Guardar en sesión y BD
            request.session['empresa_activa_id'] = empresa.id
            EmpresaActiva.objects.update_or_create(
                usuario=request.user,
                defaults={'empresa': empresa}
            )
            
            return empresa
        
        return None
    
    def is_exempt_url(self, path):
        """
        Verifica si una URL está exenta del middleware.
        """
        for exempt_url in self.exempt_urls:
            if path.startswith(exempt_url):
                return True
        return False
    
    def redirect_to_role_dashboard(self, rol):
        """
        Redirige al dashboard específico según el rol del usuario.
        """
        dashboard_urls = {
            'admin': 'empresas:admin_dashboard',
            'contador': 'empresas:contador_dashboard',  # A crear
            'operador': 'empresas:operador_dashboard',   # A crear
            'observador': 'empresas:observador_dashboard'  # A crear
        }
        
        dashboard_url = dashboard_urls.get(rol)
        if dashboard_url:
            try:
                return redirect(dashboard_url)
            except (ValueError, KeyError):
                # Si la URL no existe, redirigir al dashboard de empresas
                return redirect('empresas:empresa_list')
        
        return redirect('empresas:empresa_list')


class EmpresaFilterMixin:
    """
    Mixin para vistas que necesitan filtrar por empresa activa.
    """
    
    def get_queryset(self):
        """
        Filtra el queryset por la empresa activa.
        """
        queryset = super().get_queryset()
        
        # Solo filtrar si el modelo tiene campo empresa
        if hasattr(queryset.model, 'empresa'):
            empresa_activa = getattr(self.request, 'empresa_activa', None)
            if empresa_activa:
                queryset = queryset.filter(empresa=empresa_activa)
        
        return queryset
    
    def form_valid(self, form):
        """
        Establece la empresa activa en el formulario antes de guardar.
        """
        if hasattr(form.instance, 'empresa'):
            empresa_activa = getattr(self.request, 'empresa_activa', None)
            if empresa_activa:
                form.instance.empresa = empresa_activa
        
        return super().form_valid(form)


def empresa_requerida(view_func):
    """
    Decorador para vistas basadas en función que requieren empresa activa.
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'empresa_activa'):
            messages.error(
                request,
                'Debes seleccionar una empresa para acceder a esta función.'
            )
            return redirect(CAMBIAR_EMPRESA_URL)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def verificar_rol(roles_permitidos):
    """
    Decorador para verificar roles de usuario en la empresa activa.
    
    Args:
        roles_permitidos: Lista de roles permitidos ['admin', 'contador', 'operador']
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            rol_usuario = getattr(request, 'rol_empresa', None)
            
            if not rol_usuario or rol_usuario not in roles_permitidos:
                messages.error(
                    request,
                    'No tienes permisos para acceder a esta función.'
                )
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
