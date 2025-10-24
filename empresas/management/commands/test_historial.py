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
        
        # Buscar un usuario no administrador para la prueba
        usuario_prueba = User.objects.filter(is_superuser=False).first()
        
        if not usuario_prueba:
            self.stdout.write(self.style.ERROR('❌ No se encontró un usuario no administrador para la prueba'))
            return
        
        self.stdout.write(f'👤 Usando usuario: {usuario_prueba.username}')
        
        # Buscar una empresa para asociar
        empresa_prueba = Empresa.objects.first()
        
        if not empresa_prueba:
            self.stdout.write(self.style.ERROR('❌ No se encontró una empresa para la prueba'))
            return
        
        self.stdout.write(f'🏢 Usando empresa: {empresa_prueba.razon_social}')
        
        # Registrar algunas acciones de prueba manualmente
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
            try:
                historial = HistorialCambios.registrar_accion(
                    usuario=usuario_prueba,
                    tipo_accion=accion['tipo_accion'],
                    descripcion=accion['descripcion'],
                    empresa=empresa_prueba,
                    exitosa=True
                )
                
                if historial:
                    registros_creados += 1
                    self.stdout.write(f'✅ Registrado: {accion["descripcion"]}')
                else:
                    self.stdout.write(f'⚠️  No se registró: {accion["descripcion"]} (posiblemente es admin)')
                    
            except Exception as e:
                self.stdout.write(f'❌ Error registrando {accion["descripcion"]}: {e}')
        
        # Mostrar estadísticas
        total_registros = HistorialCambios.objects.count()
        registros_usuario = HistorialCambios.objects.filter(usuario=usuario_prueba).count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 ESTADÍSTICAS DEL HISTORIAL:'))
        self.stdout.write(f'📈 Total de registros en el sistema: {total_registros}')
        self.stdout.write(f'👤 Registros del usuario {usuario_prueba.username}: {registros_usuario}')
        self.stdout.write(f'🆕 Registros creados en esta prueba: {registros_creados}')
        
        # Mostrar los últimos 5 registros
        ultimos_registros = HistorialCambios.objects.order_by('-fecha_hora')[:5]
        
        if ultimos_registros:
            self.stdout.write(self.style.SUCCESS('\n📋 ÚLTIMOS 5 REGISTROS:'))
            for i, registro in enumerate(ultimos_registros, 1):
                self.stdout.write(
                    f'{i}. {registro.fecha_hora.strftime("%d/%m/%Y %H:%M")} - '
                    f'{registro.usuario.username} - {registro.get_tipo_accion_display()} - '
                    f'{registro.descripcion[:50]}{"..." if len(registro.descripcion) > 50 else ""}'
                )
        
        # Verificar middleware
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
        
        # Verificar señales
        self.stdout.write(self.style.SUCCESS('\n📡 VERIFICACIÓN DE SEÑALES:'))
        
        from django.db.models.signals import post_save
        
        # Verificar si las señales están conectadas
        impuesto_signals = post_save._live_receivers(sender=Impuesto)
        metodo_pago_signals = post_save._live_receivers(sender=MetodoPago)
        
        self.stdout.write(f'📊 Señales conectadas para Impuesto: {len(impuesto_signals)}')
        self.stdout.write(f'💳 Señales conectadas para MetodoPago: {len(metodo_pago_signals)}')
        
        if len(impuesto_signals) > 0 and len(metodo_pago_signals) > 0:
            self.stdout.write('✅ Las señales están conectadas correctamente')
        else:
            self.stdout.write('⚠️  Algunas señales podrían no estar conectadas')
        
        self.stdout.write(self.style.SUCCESS('\n🎉 Prueba del historial completada!'))
        self.stdout.write('💡 Ahora puedes:')
        self.stdout.write('   1. Crear un impuesto desde la interfaz web')
        self.stdout.write('   2. Editar un método de pago')
        self.stdout.write('   3. Verificar el historial en /empresas/admin/historial/')
        self.stdout.write('   4. O en el Admin Django: /admin/empresas/historialcambios/')
