"""
Comando para probar el sistema de historial de cambios
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from empresas.models import HistorialCambios, Empresa, EmpresaActiva
from catalogos.models import Impuesto, MetodoPago


class Command(BaseCommand):
    help = 'Prueba el sistema de historial de cambios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Iniciando prueba del historial de cambios...'))
        
        usuario_prueba = self._obtener_usuario_prueba()
        if not usuario_prueba:
            return
        
        empresa_prueba = self._obtener_empresa_prueba()
        if not empresa_prueba:
            return
        
        registros_creados = self._registrar_acciones_prueba(usuario_prueba, empresa_prueba)
        self._mostrar_estadisticas(usuario_prueba, registros_creados)
        self._mostrar_ultimos_registros()
        self._verificar_middleware()
        self._verificar_senales()
        self._mostrar_mensaje_final()
    
    def _obtener_usuario_prueba(self):
        """Busca un usuario no administrador para la prueba"""
        usuario_prueba = User.objects.filter(is_superuser=False).first()
        
        if not usuario_prueba:
            self.stdout.write(self.style.ERROR('❌ No se encontró un usuario no administrador para la prueba'))
            return None
        
        self.stdout.write(f'👤 Usando usuario: {usuario_prueba.username}')
        return usuario_prueba
    
    def _obtener_empresa_prueba(self):
        """Busca una empresa para asociar"""
        empresa_prueba = Empresa.objects.first()
        
        if not empresa_prueba:
            self.stdout.write(self.style.ERROR('❌ No se encontró una empresa para la prueba'))
            return None
        
        self.stdout.write(f'🏢 Usando empresa: {empresa_prueba.razon_social}')
        return empresa_prueba
    
    def _registrar_acciones_prueba(self, usuario_prueba, empresa_prueba):
        """Registra acciones de prueba manualmente"""
        acciones_prueba = [
            {
                'tipo_accion': 'configuracion_cambiar',
                'descripcion': 'Impuesto de prueba creado desde comando de testing',
            },
            {
                'tipo_accion': 'configuracion_cambiar', 
                'descripcion': 'Método de pago de prueba creado desde comando de testing',
            },
            {
                'tipo_accion': 'usuario_login',
                'descripcion': 'Inicio de sesión de prueba desde comando de testing',
            }
        ]
        
        registros_creados = 0
        
        for accion in acciones_prueba:
            historial = self._registrar_accion_individual(usuario_prueba, empresa_prueba, accion)
            if historial:
                registros_creados += 1
        
        return registros_creados
    
    def _registrar_accion_individual(self, usuario_prueba, empresa_prueba, accion):
        """Registra una acción individual y muestra el resultado"""
        try:
            historial = HistorialCambios.registrar_accion(
                usuario=usuario_prueba,
                tipo_accion=accion['tipo_accion'],
                descripcion=accion['descripcion'],
                empresa=empresa_prueba,
                exitosa=True
            )
            
            if historial:
                self.stdout.write(f'✅ Registrado: {accion["descripcion"]}')
                return historial
            else:
                self.stdout.write(f'⚠️  No se registró: {accion["descripcion"]} (posiblemente es admin)')
                return None
                    
        except Exception as e:
            self.stdout.write(f'❌ Error registrando {accion["descripcion"]}: {e}')
            return None
    
    def _mostrar_estadisticas(self, usuario_prueba, registros_creados):
        """Muestra estadísticas del historial"""
        total_registros = HistorialCambios.objects.count()
        registros_usuario = HistorialCambios.objects.filter(usuario=usuario_prueba).count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 ESTADÍSTICAS DEL HISTORIAL:'))
        self.stdout.write(f'📈 Total de registros en el sistema: {total_registros}')
        self.stdout.write(f'👤 Registros del usuario {usuario_prueba.username}: {registros_usuario}')
        self.stdout.write(f'🆕 Registros creados en esta prueba: {registros_creados}')
    
    def _mostrar_ultimos_registros(self):
        """Muestra los últimos 5 registros del historial"""
        ultimos_registros = HistorialCambios.objects.order_by('-fecha_hora')[:5]
        
        if not ultimos_registros:
            return
        
        self.stdout.write(self.style.SUCCESS('\n📋 ÚLTIMOS 5 REGISTROS:'))
        for i, registro in enumerate(ultimos_registros, 1):
            descripcion = registro.descripcion[:50]
            if len(registro.descripcion) > 50:
                descripcion += "..."
            
            self.stdout.write(
                f'{i}. {registro.fecha_hora.strftime("%d/%m/%Y %H:%M")} - '
                f'{registro.usuario.username} - {registro.get_tipo_accion_display()} - '
                f'{descripcion}'
            )
    
    def _verificar_middleware(self):
        """Verifica si los middleware están configurados"""
        self.stdout.write(self.style.SUCCESS('\n🔧 VERIFICACIÓN DEL MIDDLEWARE:'))
        
        from django.conf import settings
        middleware_historial = [
            'empresas.middleware_historial.ThreadLocalMiddleware',
            'empresas.middleware_historial.HistorialCambiosMiddleware'
        ]
        
        for middleware in middleware_historial:
            if middleware in settings.MIDDLEWARE:
                self.stdout.write(f'✅ {middleware} está configurado')
            else:
                self.stdout.write(f'❌ {middleware} NO está configurado')
    
    def _verificar_senales(self):
        """Verifica si las señales están conectadas"""
        self.stdout.write(self.style.SUCCESS('\n📡 VERIFICACIÓN DE SEÑALES:'))
        
        from django.db.models.signals import post_save
        
        impuesto_signals = post_save._live_receivers(sender=Impuesto)
        metodo_pago_signals = post_save._live_receivers(sender=MetodoPago)
        
        self.stdout.write(f'📊 Señales conectadas para Impuesto: {len(impuesto_signals)}')
        self.stdout.write(f'💳 Señales conectadas para MetodoPago: {len(metodo_pago_signals)}')
        
        if len(impuesto_signals) > 0 and len(metodo_pago_signals) > 0:
            self.stdout.write('✅ Las señales están conectadas correctamente')
        else:
            self.stdout.write('⚠️  Algunas señales podrían no estar conectadas')
    
    def _mostrar_mensaje_final(self):
        """Muestra el mensaje final con instrucciones"""
        self.stdout.write(self.style.SUCCESS('\n🎉 Prueba del historial completada!'))
        self.stdout.write('💡 Ahora puedes:')
        self.stdout.write('   1. Crear un impuesto desde la interfaz web')
        self.stdout.write('   2. Editar un método de pago')
        self.stdout.write('   3. Verificar el historial en /empresas/admin/historial/')
        self.stdout.write('   4. O en el Admin Django: /admin/empresas/historialcambios/')
