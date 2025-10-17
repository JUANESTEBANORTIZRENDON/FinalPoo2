"""
Vistas personalizadas para el panel de administración
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.models import User
from .models import PerfilUsuario


@staff_member_required
def admin_dashboard(request):
    """Vista personalizada del dashboard del admin"""
    
    # Estadísticas básicas
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'total_profiles': PerfilUsuario.objects.count(),
        'admin_users': User.objects.filter(is_superuser=True).count(),
        'staff_users': User.objects.filter(is_staff=True, is_superuser=False).count(),
    }
    
    # Usuarios recientes
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Perfiles por ciudad (top 5)
    from django.db.models import Count
    cities_stats = PerfilUsuario.objects.values('ciudad').annotate(
        count=Count('ciudad')
    ).order_by('-count')[:5]
    
    # Tipos de documento más comunes
    doc_types_stats = PerfilUsuario.objects.values('tipo_documento').annotate(
        count=Count('tipo_documento')
    ).order_by('-count')
    
    context = {
        'title': 'Dashboard S_CONTABLE',
        'stats': stats,
        'recent_users': recent_users,
        'cities_stats': cities_stats,
        'doc_types_stats': doc_types_stats,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)
