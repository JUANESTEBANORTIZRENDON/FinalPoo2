"""
Vistas personalizadas para el panel de administración Django
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from accounts.models import PerfilUsuario
from empresas.models import Empresa


@staff_member_required
def admin_index(request):
    """
    Vista personalizada para el index del admin con estadísticas
    """
    # Obtener estadísticas del sistema
    try:
        total_users = User.objects.count()
        total_companies = Empresa.objects.count()
        total_profiles = PerfilUsuario.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_users = User.objects.filter(is_superuser=True).count()
        system_health = "OK" if total_users > 0 else "ALERTA"
    except Exception as e:
        print(f"Error al obtener estadísticas: {e}")
        total_users = 0
        total_companies = 0
        total_profiles = 0
        active_users = 0
        admin_users = 0
        system_health = "ERROR"
    
    # Obtener el contexto estándar del admin
    context = {
        **admin.site.each_context(request),
        'title': admin.site.index_title,
        'total_users': total_users,
        'total_companies': total_companies,
        'total_profiles': total_profiles,
        'active_users': active_users,
        'admin_users': admin_users,
        'system_health': system_health,
    }
    
    return TemplateResponse(request, 'admin/index.html', context)
