from django.apps import AppConfig


class CatalogosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogos'
    
    def ready(self):
        """Conectar señales cuando la app esté lista"""
        from django.db.models.signals import post_save, post_delete
        from empresas.middleware_historial import HistorialCambiosSignalHandler
        from .models import Tercero, Impuesto, MetodoPago, Producto
        
        # Conectar señales para todos los modelos de catálogos
        modelos_catalogos = [Tercero, Impuesto, MetodoPago, Producto]
        
        for modelo in modelos_catalogos:
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
