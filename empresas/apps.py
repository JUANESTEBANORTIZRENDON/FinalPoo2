from django.apps import AppConfig


class EmpresasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'empresas'
    
    def ready(self):
        """Conectar señales cuando la app esté lista"""
        from django.db.models.signals import post_save, post_delete
        from .middleware_historial import HistorialCambiosSignalHandler
        from .models import Empresa, PerfilEmpresa, EmpresaActiva
        
        # Conectar señales para modelos de empresas
        modelos_empresas = [Empresa, PerfilEmpresa, EmpresaActiva]
        
        for modelo in modelos_empresas:
            post_save.connect(
                HistorialCambiosSignalHandler.registrar_cambio_modelo,
                sender=modelo,
                dispatch_uid=f'historial_{modelo.__name__.lower()}_save'
            )
            
            post_delete.connect(
                HistorialCambiosSignalHandler.registrar_eliminacion_modelo,
                sender=modelo,
                dispatch_uid=f'historial_{modelo.__name__.lower()}_delete'
            )
