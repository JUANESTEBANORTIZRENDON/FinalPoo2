"""
Middleware para capturar automáticamente las acciones de los usuarios
y registrarlas en el historial de cambios
"""
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import HistorialCambios, EmpresaActiva

# Constantes para evitar duplicación de literales de descripciones
DESC_TERCERO_CREADO = 'Tercero creado'
DESC_IMPUESTO_CREADO = 'Impuesto creado'
DESC_METODO_PAGO_CREADO = 'Método de pago creado'
DESC_PRODUCTO_CREADO = 'Producto creado'
DESC_FACTURA_CREADA = 'Factura creada'

# Constantes para rutas comunes
PATH_TERCEROS = '/terceros/'
PATH_PRODUCTOS = '/productos/'
PATH_ASIENTOS = '/asientos/'


class HistorialCambiosMiddleware(MiddlewareMixin):
    """
    Middleware que registra automáticamente las acciones de los usuarios
    en el sistema (excepto administradores del holding)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Registra el tiempo de inicio de la petición"""
        request._historial_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Procesa la respuesta y registra la acción si es necesaria"""
        
        # Solo procesar si el usuario está autenticado
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # No registrar acciones de superusuarios/administradores del holding
        if request.user.is_superuser:
            return response
        
        # No registrar peticiones de archivos estáticos, admin Django, o API
        if self._should_skip_logging(request):
            return response
        
        # Determinar si la acción fue exitosa
        exitosa = 200 <= response.status_code < 400
        mensaje_error = None
        
        if not exitosa:
            mensaje_error = f"HTTP {response.status_code}"
            if hasattr(response, 'reason_phrase'):
                mensaje_error += f" - {response.reason_phrase}"
        
        # Obtener empresa activa del usuario
        empresa = self._get_empresa_activa(request.user)
        
        # Determinar el tipo de acción y descripción
        tipo_accion, descripcion = self._determinar_accion(request, response)
        
        if tipo_accion:
            try:
                HistorialCambios.registrar_accion(
                    usuario=request.user,
                    tipo_accion=tipo_accion,
                    descripcion=descripcion,
                    empresa=empresa,
                    request=request,
                    exitosa=exitosa,
                    mensaje_error=mensaje_error
                )
            except Exception as e:
                # No queremos que errores en el logging rompan la aplicación
                print(f"Error registrando historial: {e}")
        
        return response
    
    def _should_skip_logging(self, request):
        """Determina si se debe omitir el logging para esta petición"""
        path = request.path.lower()
        
        # Omitir archivos estáticos
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2', '.ttf']
        if any(path.endswith(ext) for ext in static_extensions):
            return True
        
        # Omitir rutas específicas
        skip_paths = [
            '/admin/',  # Admin de Django
            '/api/',    # API REST
            '/static/', # Archivos estáticos
            '/media/',  # Archivos de media
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
        ]
        
        if any(path.startswith(skip_path) for skip_path in skip_paths):
            return True
        
        # Omitir peticiones AJAX de polling o heartbeat
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            ajax_skip_patterns = [
                'heartbeat',
                'ping',
                'status',
                'poll',
            ]
            if any(pattern in path for pattern in ajax_skip_patterns):
                return True
        
        return False
    
    def _get_empresa_activa(self, user):
        """Obtiene la empresa activa del usuario"""
        try:
            empresa_activa = EmpresaActiva.objects.get(usuario=user)
            return empresa_activa.empresa
        except EmpresaActiva.DoesNotExist:
            return None
    
    def _determinar_accion(self, request, response):
        """Determina el tipo de acción y descripción basado en la petición"""
        path = request.path
        method = request.method
        
        # Mapeo de rutas a tipos de acción
        route_mappings = {
            # Acciones de usuarios
            '/accounts/login/': ('usuario_login', 'Inicio de sesión'),
            '/accounts/logout/': ('usuario_logout', 'Cierre de sesión'),
            '/accounts/perfil/': ('usuario_perfil_actualizado', 'Perfil actualizado'),
            
            # Acciones de empresas
            '/empresas/seleccionar/': ('usuario_cambio_empresa', 'Cambio de empresa activa'),
            '/empresas/cambiar-empresa/': ('usuario_cambio_empresa', 'Cambio de empresa activa'),
            
            # Acciones de catálogos - Terceros
            '/catalogos/terceros/crear/': ('tercero_crear', DESC_TERCERO_CREADO),
            '/catalogos/terceros/nuevo/': ('tercero_crear', DESC_TERCERO_CREADO),
            
            # Acciones de catálogos - Impuestos
            '/catalogos/impuestos/crear/': ('configuracion_cambiar', DESC_IMPUESTO_CREADO),
            '/catalogos/impuestos/nuevo/': ('configuracion_cambiar', DESC_IMPUESTO_CREADO),
            
            # Acciones de catálogos - Métodos de pago
            '/catalogos/metodos-pago/crear/': ('configuracion_cambiar', DESC_METODO_PAGO_CREADO),
            '/catalogos/metodos-pago/nuevo/': ('configuracion_cambiar', DESC_METODO_PAGO_CREADO),
            
            # Acciones de catálogos - Productos
            '/catalogos/productos/crear/': ('producto_crear', DESC_PRODUCTO_CREADO),
            '/catalogos/productos/nuevo/': ('producto_crear', DESC_PRODUCTO_CREADO),
            
            # Acciones de facturación
            '/facturacion/facturas/crear/': ('factura_crear', DESC_FACTURA_CREADA),
            '/facturacion/facturas/nueva/': ('factura_crear', DESC_FACTURA_CREADA),
            
            # Acciones de tesorería
            '/tesoreria/pagos/crear/': ('pago_crear', 'Pago registrado'),
            '/tesoreria/cobros/crear/': ('cobro_crear', 'Cobro registrado'),
            
            # Acciones de contabilidad
            '/contabilidad/asientos/crear/': ('asiento_crear', 'Asiento contable creado'),
            
            # Acciones de reportes
            '/reportes/': ('reporte_generar', 'Reporte generado'),
        }
        
        # Buscar coincidencia exacta primero
        if path in route_mappings:
            return route_mappings[path]
        
        # Buscar patrones más específicos
        if method == 'POST':
            if '/crear/' in path:
                return self._determinar_accion_crear(path)
            elif '/editar/' in path:
                return self._determinar_accion_editar(path)
            elif '/eliminar/' in path:
                return self._determinar_accion_eliminar(path)
        
        elif method == 'GET' and '/reportes/' in path:
            return ('reporte_generar', f'Consulta de reporte: {path}')
        
        # Acciones de error
        if not (200 <= response.status_code < 400):
            if response.status_code == 403:
                return ('acceso_denegado', f'Acceso denegado a: {path}')
            elif response.status_code >= 500:
                return ('error_sistema', f'Error del sistema en: {path}')
        
        # Si no se puede determinar una acción específica, no registrar
        return None, None
    
    def _determinar_accion_crear(self, path):
        """Determina la acción de creación basada en la ruta"""
        if PATH_TERCEROS in path:
            return ('tercero_crear', DESC_TERCERO_CREADO)
        elif '/impuestos/' in path:
            return ('configuracion_cambiar', DESC_IMPUESTO_CREADO)
        elif '/metodos-pago/' in path:
            return ('configuracion_cambiar', DESC_METODO_PAGO_CREADO)
        elif PATH_PRODUCTOS in path:
            return ('producto_crear', DESC_PRODUCTO_CREADO)
        elif '/facturas/' in path:
            return ('factura_crear', DESC_FACTURA_CREADA)
        elif '/pagos/' in path:
            return ('pago_crear', 'Pago registrado')
        elif '/cobros/' in path:
            return ('cobro_crear', 'Cobro registrado')
        elif PATH_ASIENTOS in path:
            return ('asiento_crear', 'Asiento contable creado')
        elif '/empresas/' in path:
            return ('empresa_crear', 'Empresa creada')
        else:
            return ('configuracion_cambiar', f'Elemento creado en: {path}')
    
    def _determinar_accion_editar(self, path):
        """Determina la acción de edición basada en la ruta"""
        if PATH_TERCEROS in path:
            return ('tercero_editar', 'Tercero editado')
        elif '/impuestos/' in path:
            return ('configuracion_cambiar', 'Impuesto editado')
        elif '/metodos-pago/' in path:
            return ('configuracion_cambiar', 'Método de pago editado')
        elif PATH_PRODUCTOS in path:
            return ('producto_editar', 'Producto editado')
        elif '/facturas/' in path:
            return ('factura_editar', 'Factura editada')
        elif '/pagos/' in path:
            return ('pago_editar', 'Pago editado')
        elif '/cobros/' in path:
            return ('cobro_editar', 'Cobro editado')
        elif PATH_ASIENTOS in path:
            return ('asiento_editar', 'Asiento contable editado')
        elif '/empresas/' in path:
            return ('empresa_editar', 'Empresa editada')
        else:
            return ('configuracion_cambiar', f'Elemento editado en: {path}')
    
    def _determinar_accion_eliminar(self, path):
        """Determina la acción de eliminación basada en la ruta"""
        if PATH_TERCEROS in path:
            return ('tercero_eliminar', 'Tercero eliminado')
        elif PATH_PRODUCTOS in path:
            return ('producto_eliminar', 'Producto eliminado')
        elif PATH_ASIENTOS in path:
            return ('asiento_eliminar', 'Asiento contable eliminado')
        else:
            return ('configuracion_cambiar', f'Elemento eliminado en: {path}')


class HistorialCambiosSignalHandler:
    """
    Manejador de señales para registrar cambios en modelos específicos
    usando las señales post_save y post_delete de Django
    """
    
    @staticmethod
    def registrar_cambio_modelo(sender, instance, created, **kwargs):
        """
        Registra cambios en modelos cuando se guardan
        """
        # Obtener el usuario actual del contexto (si está disponible)
        # Esto requiere que el middleware de threading esté configurado
        from threading import current_thread
        
        request = getattr(current_thread(), 'request', None)
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        # No registrar cambios de administradores del holding
        if request.user.is_superuser:
            return
        
        # Determinar el tipo de acción
        modelo_nombre = sender.__name__.lower()
        
        if created:
            tipo_accion = f'{modelo_nombre}_crear'
            descripcion = f'{sender._meta.verbose_name} creado: {str(instance)}'
        else:
            tipo_accion = f'{modelo_nombre}_editar'
            descripcion = f'{sender._meta.verbose_name} editado: {str(instance)}'
        
        # Obtener empresa activa
        try:
            empresa_activa = EmpresaActiva.objects.get(usuario=request.user)
            empresa = empresa_activa.empresa
        except EmpresaActiva.DoesNotExist:
            empresa = None
        
        # Registrar la acción
        try:
            HistorialCambios.registrar_accion(
                usuario=request.user,
                tipo_accion=tipo_accion,
                descripcion=descripcion,
                empresa=empresa,
                modelo_afectado=sender.__name__,
                objeto_id=instance.pk,
                request=request
            )
        except Exception as e:
            print(f"Error registrando cambio de modelo: {e}")
    
    @staticmethod
    def registrar_eliminacion_modelo(sender, instance, **kwargs):
        """
        Registra eliminaciones de modelos
        """
        from threading import current_thread
        
        request = getattr(current_thread(), 'request', None)
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            return
        
        # No registrar cambios de administradores del holding
        if request.user.is_superuser:
            return
        
        modelo_nombre = sender.__name__.lower()
        tipo_accion = f'{modelo_nombre}_eliminar'
        descripcion = f'{sender._meta.verbose_name} eliminado: {str(instance)}'
        
        # Obtener empresa activa
        try:
            empresa_activa = EmpresaActiva.objects.get(usuario=request.user)
            empresa = empresa_activa.empresa
        except EmpresaActiva.DoesNotExist:
            empresa = None
        
        # Registrar la acción
        try:
            HistorialCambios.registrar_accion(
                usuario=request.user,
                tipo_accion=tipo_accion,
                descripcion=descripcion,
                empresa=empresa,
                modelo_afectado=sender.__name__,
                objeto_id=instance.pk,
                request=request
            )
        except Exception as e:
            print(f"Error registrando eliminación de modelo: {e}")


# Middleware para agregar el request al thread local
class ThreadLocalMiddleware(MiddlewareMixin):
    """
    Middleware para hacer el request disponible en el thread local
    para que las señales puedan acceder a él
    """
    
    def process_request(self, request):
        from threading import current_thread
        current_thread().request = request
        return None
    
    def process_response(self, request, response):
        from threading import current_thread
        if hasattr(current_thread(), 'request'):
            delattr(current_thread(), 'request')
        return response
