"""
Utilidades y helpers comunes para reducir duplicación
Compatibles con Django 5.x
"""
from django.contrib.auth.models import User
from django.db.models import Count
from accounts.models import PerfilUsuario
from empresas.models import Empresa


def get_user_stats():
    """
    Obtiene estadísticas de usuarios del sistema
    Centraliza la lógica duplicada en varios archivos
    
    Returns:
        dict: Diccionario con estadísticas de usuarios
    """
    try:
        return {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'inactive_users': User.objects.filter(is_active=False).count(),
            'total_profiles': PerfilUsuario.objects.count(),
            'admin_users': User.objects.filter(is_superuser=True).count(),
            'staff_users': User.objects.filter(is_staff=True, is_superuser=False).count(),
        }
    except Exception:
        # Retornar valores por defecto en caso de error
        return {
            'total_users': 0,
            'active_users': 0,
            'inactive_users': 0,
            'total_profiles': 0,
            'admin_users': 0,
            'staff_users': 0,
        }


def get_empresa_stats():
    """
    Obtiene estadísticas de empresas del sistema
    
    Returns:
        dict: Diccionario con estadísticas de empresas
    """
    try:
        return {
            'total_companies': Empresa.objects.count(),
            'active_companies': Empresa.objects.filter(activa=True).count(),
            'inactive_companies': Empresa.objects.filter(activa=False).count(),
        }
    except Exception:
        return {
            'total_companies': 0,
            'active_companies': 0,
            'inactive_companies': 0,
        }


def get_profile_stats():
    """
    Obtiene estadísticas de perfiles de usuario
    
    Returns:
        dict: Estadísticas con ciudades y tipos de documento más comunes
    """
    try:
        cities_stats = PerfilUsuario.objects.values('ciudad').annotate(
            count=Count('ciudad')
        ).order_by('-count')[:5]
        
        doc_types_stats = PerfilUsuario.objects.values('tipo_documento').annotate(
            count=Count('tipo_documento')
        ).order_by('-count')[:5]
        
        return {
            'cities_stats': list(cities_stats),
            'doc_types_stats': list(doc_types_stats),
        }
    except Exception:
        return {
            'cities_stats': [],
            'doc_types_stats': [],
        }


def get_recent_users(limit=5):
    """
    Obtiene los usuarios más recientes
    
    Args:
        limit (int): Número de usuarios a retornar
        
    Returns:
        QuerySet: Usuarios ordenados por fecha de creación
    """
    try:
        return User.objects.order_by('-date_joined')[:limit]
    except Exception:
        return User.objects.none()


def get_complete_stats():
    """
    Obtiene todas las estadísticas del sistema de forma consolidada
    
    Returns:
        dict: Diccionario con todas las estadísticas
    """
    stats = {}
    stats.update(get_user_stats())
    stats.update(get_empresa_stats())
    profile_stats = get_profile_stats()
    
    return {
        **stats,
        'recent_users': get_recent_users(),
        'cities_stats': profile_stats['cities_stats'],
        'doc_types_stats': profile_stats['doc_types_stats'],
    }


def validate_user_data(username, email):
    """
    Validación común de datos de usuario
    
    Args:
        username (str): Nombre de usuario
        email (str): Email del usuario
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or not email:
        return False, 'El nombre de usuario y el email son requeridos.'
    
    if User.objects.filter(username=username).exists():
        return False, f'El nombre de usuario "{username}" ya existe.'
    
    if User.objects.filter(email=email).exists():
        return False, f'El email "{email}" ya está registrado.'
    
    return True, None


def validate_password(password, password_confirm):
    """
    Validación común de contraseñas
    
    Args:
        password (str): Contraseña
        password_confirm (str): Confirmación de contraseña
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, 'La contraseña es requerida.'
    
    if len(password) < 8:
        return False, 'La contraseña debe tener al menos 8 caracteres.'
    
    if password != password_confirm:
        return False, 'Las contraseñas no coinciden.'
    
    return True, None


def build_queryset_filters(queryset, filters_dict):
    """
    Construye filtros dinámicos para un queryset
    Reduce duplicación en vistas de lista con múltiples filtros
    
    Args:
        queryset: QuerySet base
        filters_dict: Diccionario con {campo: valor} para filtrar
        
    Returns:
        QuerySet: QuerySet filtrado
    """
    for field, value in filters_dict.items():
        if value:
            queryset = queryset.filter(**{field: value})
    
    return queryset
