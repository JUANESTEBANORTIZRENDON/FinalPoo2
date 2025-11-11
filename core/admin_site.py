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
        
        # Obtener estadísticas del sistema usando utilidad centralizada
        try:
            from core.utils import get_complete_stats
            
            stats = get_complete_stats()
            system_health = "OK" if stats['total_users'] > 0 else "ALERTA"
            
            context.update({
                'total_users': stats['total_users'],
                'total_companies': stats.get('total_companies', 0),
                'total_profiles': stats.get('total_profiles', 0),
                'active_users': stats['active_users'],
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
        app_list = self.get_app_list(request)
        structure = self._create_sidebar_sections()
        app_dict = {app['app_label']: app for app in app_list}
        
        self._populate_sidebar_models(structure, app_dict)
        
        # Filtrar secciones vacías (sin modelos)
        return [section for section in structure if section['models']]
    
    def _create_sidebar_sections(self):
        """Crea la estructura base de secciones del sidebar"""
        return [
            {'name': 'Gestión de Usuarios', 'icon': 'fa-users', 
             'apps': ['auth', 'accounts'], 'models': []},
            {'name': 'Empresas', 'icon': 'fa-building', 
             'apps': ['empresas'], 'models': []},
            {'name': 'Catálogos', 'icon': 'fa-boxes', 
             'apps': ['catalogos'], 'models': []},
            {'name': 'Facturación', 'icon': 'fa-file-invoice', 
             'apps': ['facturacion'], 'models': []},
            {'name': 'Tesorería', 'icon': 'fa-piggy-bank', 
             'apps': ['tesoreria'], 'models': []},
            {'name': 'Contabilidad', 'icon': 'fa-book', 
             'apps': ['contabilidad'], 'models': []},
            {'name': 'Reportes', 'icon': 'fa-chart-line', 
             'apps': ['reportes'], 'models': []},
            {'name': 'API REST', 'icon': 'fa-code', 
             'apps': ['api'], 'models': []},
            {'name': 'Ventas', 'icon': 'fa-shopping-cart', 
             'apps': ['ventas'], 'models': []},
            {'name': 'Herramientas de Desarrollo', 'icon': 'fa-wrench', 
             'apps': ['admin', 'sessions', 'contenttypes'], 'models': []},
        ]
    
    def _populate_sidebar_models(self, structure, app_dict):
        """Mapea los modelos de cada app a su sección correspondiente"""
        for section in structure:
            for app_label in section['apps']:
                if app_label in app_dict:
                    self._add_app_models_to_section(section, app_dict[app_label], app_label)
    
    def _add_app_models_to_section(self, section, app_data, app_label):
        """Agrega los modelos de una app a una sección del sidebar"""
        for model in app_data.get('models', []):
            if self._has_view_permission(model):
                section['models'].append(self._create_model_entry(model, app_label))
    
    def _has_view_permission(self, model):
        """Verifica si el usuario tiene permisos de visualización o cambio"""
        perms = model.get('perms', {})
        return perms.get('view', False) or perms.get('change', False)
    
    def _create_model_entry(self, model, app_label):
        """Crea la entrada de un modelo para el sidebar"""
        perms = model.get('perms', {})
        return {
            'name': model['name'],
            'object_name': model['object_name'],
            'admin_url': model.get('admin_url'),
            'add_url': model.get('add_url') if perms.get('add', False) else None,
            'view_perm': perms.get('view', False),
            'add_perm': perms.get('add', False),
            'app_label': app_label,
        }
    
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
