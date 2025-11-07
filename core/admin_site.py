"""
AdminSite personalizado para S_CONTABLE
Incluye estadísticas del sistema y estructura jerárquica del sidebar
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class ContableAdminSite(AdminSite):
    """
    AdminSite personalizado que:
    1. Muestra estadísticas en el dashboard
    2. Organiza el sidebar por áreas funcionales del sistema
    3. Respeta permisos de usuario
    """
    
    # Configuración básica
    site_header = "🏢 S_CONTABLE - Panel de Desarrollador"
    site_title = "S_CONTABLE Admin"
    index_title = "🇨🇴 Sistema Contable Colombiano - Panel de Control"
    index_template = "admin/index.html"
    
    def each_context(self, request):
        """
        Agregar estadísticas y datos personalizados al contexto de todas las vistas del admin
        """
        context = super().each_context(request)
        
        # Obtener estadísticas del sistema
        try:
            from accounts.models import PerfilUsuario
            from empresas.models import Empresa, PerfilEmpresa
            
            total_users = User.objects.count()
            total_companies = Empresa.objects.count()
            total_profiles = PerfilEmpresa.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            system_health = "OK" if total_users > 0 else "ALERTA"
            
            context.update({
                'total_users': total_users,
                'total_companies': total_companies,
                'total_profiles': total_profiles,
                'active_users': active_users,
                'system_health': system_health,
            })
        except Exception as e:
            print(f"⚠️ Error al obtener estadísticas: {e}")
            context.update({
                'total_users': 0,
                'total_companies': 0,
                'total_profiles': 0,
                'active_users': 0,
                'system_health': "ERROR",
            })
        
        # Agregar estructura del sidebar
        context['sidebar_structure'] = self.get_sidebar_structure(request)
        
        return context
    
    def get_sidebar_structure(self, request):
        """
        Retorna la estructura jerárquica del sidebar organizada por áreas funcionales
        """
        # Obtener las apps registradas
        app_list = self.get_app_list(request)
        
        # Definir la estructura del sidebar por secciones
        structure = [
            {
                'name': 'Gestión de Usuarios',
                'icon': 'fa-users',
                'apps': ['auth', 'accounts'],
                'models': []
            },
            {
                'name': 'Empresas',
                'icon': 'fa-building',
                'apps': ['empresas'],
                'models': []
            },
            {
                'name': 'Catálogos',
                'icon': 'fa-boxes',
                'apps': ['catalogos'],
                'models': []
            },
            {
                'name': 'Facturación',
                'icon': 'fa-file-invoice',
                'apps': ['facturacion'],
                'models': []
            },
            {
                'name': 'Tesorería',
                'icon': 'fa-piggy-bank',
                'apps': ['tesoreria'],
                'models': []
            },
            {
                'name': 'Contabilidad',
                'icon': 'fa-book',
                'apps': ['contabilidad'],
                'models': []
            },
            {
                'name': 'Reportes',
                'icon': 'fa-chart-line',
                'apps': ['reportes'],
                'models': []
            },
            {
                'name': 'API REST',
                'icon': 'fa-code',
                'apps': ['api'],
                'models': []
            },
            {
                'name': 'Ventas',
                'icon': 'fa-shopping-cart',
                'apps': ['ventas'],
                'models': []
            },
            {
                'name': 'Herramientas de Desarrollo',
                'icon': 'fa-wrench',
                'apps': ['admin', 'sessions', 'contenttypes'],
                'models': []
            },
        ]
        
        # Mapear los modelos de cada app a su sección correspondiente
        app_dict = {app['app_label']: app for app in app_list}
        
        for section in structure:
            for app_label in section['apps']:
                if app_label in app_dict:
                    app_data = app_dict[app_label]
                    # Agregar los modelos de esta app a la sección
                    for model in app_data.get('models', []):
                        # Verificar permisos
                        if model.get('perms', {}).get('view', False) or \
                           model.get('perms', {}).get('change', False):
                            section['models'].append({
                                'name': model['name'],
                                'object_name': model['object_name'],
                                'admin_url': model.get('admin_url'),
                                'add_url': model.get('add_url') if model.get('perms', {}).get('add', False) else None,
                                'view_perm': model.get('perms', {}).get('view', False),
                                'add_perm': model.get('perms', {}).get('add', False),
                                'app_label': app_label,
                            })
        
        # Filtrar secciones vacías (sin modelos)
        structure = [s for s in structure if s['models']]
        
        return structure
    
    def get_app_list(self, request):
        """
        Retorna la lista de aplicaciones ordenada según nuestra estructura
        """
        app_list = super().get_app_list(request)
        
        # Orden deseado de las apps
        app_order = [
            'auth',
            'accounts',
            'empresas',
            'catalogos',
            'facturacion',
            'tesoreria',
            'contabilidad',
            'reportes',
            'api',
            'ventas',
            'sessions',
            'contenttypes',
        ]
        
        # Crear un diccionario para acceso rápido
        app_dict = {app['app_label']: app for app in app_list}
        
        # Reordenar según app_order
        ordered_list = []
        for app_label in app_order:
            if app_label in app_dict:
                ordered_list.append(app_dict[app_label])
        
        # Agregar apps que no estén en app_order al final
        for app in app_list:
            if app['app_label'] not in app_order:
                ordered_list.append(app)
        
        return ordered_list


# Instancia global del AdminSite personalizado
# Usar 'admin' como namespace para mantener compatibilidad con templates
admin_site = ContableAdminSite(name='admin')
