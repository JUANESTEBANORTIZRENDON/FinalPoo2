"""
Vistas personalizadas para el panel de administración
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.decorators.http import require_safe
from core.utils import get_complete_stats


@staff_member_required
@require_safe
def admin_dashboard(request):
    """Vista personalizada del dashboard del admin"""
    
    # Obtener todas las estadísticas de forma centralizada
    stats_data = get_complete_stats()
    
    context = {
        'title': 'Dashboard S_CONTABLE',
        'stats': {
            'total_users': stats_data['total_users'],
            'active_users': stats_data['active_users'],
            'inactive_users': stats_data['inactive_users'],
            'total_profiles': stats_data['total_profiles'],
            'admin_users': stats_data['admin_users'],
            'staff_users': stats_data['staff_users'],
        },
        'recent_users': stats_data['recent_users'],
        'cities_stats': stats_data['cities_stats'],
        'doc_types_stats': stats_data['doc_types_stats'],
    }
    
    return render(request, 'admin/custom_dashboard.html', context)
