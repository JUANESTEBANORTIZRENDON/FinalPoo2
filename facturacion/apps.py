from django.apps import AppConfig


class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'facturacion'
    
    def ready(self):
        """Conectar señales cuando la app esté lista"""
        from django.db.models.signals import post_save, post_delete
        from empresas.middleware_historial import HistorialCambiosSignalHandler
        from .models import Factura, FacturaDetalle
        
        # Conectar señales para modelos de facturación
        modelos_facturacion = [Factura, FacturaDetalle]
        
        for modelo in modelos_facturacion:
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
