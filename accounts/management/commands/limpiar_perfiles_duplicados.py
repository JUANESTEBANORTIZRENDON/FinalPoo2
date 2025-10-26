"""
Comando para limpiar perfiles de usuario duplicados
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import PerfilUsuario
from django.db import transaction


class Command(BaseCommand):
    help = 'Limpia perfiles de usuario duplicados y crea perfiles faltantes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar qué se haría sin hacer cambios reales',
        )

    def handle(self, *args, **options):
        """Punto de entrada principal del comando"""
        dry_run = options['dry_run']
        
        self._mostrar_mensaje_inicial(dry_run)
        self._crear_perfiles_faltantes(dry_run)
        self._eliminar_perfiles_duplicados(dry_run)
        self._eliminar_perfiles_huerfanos(dry_run)
        self._mostrar_estadisticas_finales(dry_run)
    
    def _mostrar_mensaje_inicial(self, dry_run):
        """Muestra el mensaje inicial según el modo de ejecución"""
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: Solo mostrando qué se haría...'))
        else:
            self.stdout.write(self.style.SUCCESS('🧹 Iniciando limpieza de perfiles...'))
    
    def _crear_perfiles_faltantes(self, dry_run):
        """Crea perfiles para usuarios que no tienen uno"""
        usuarios_sin_perfil = User.objects.filter(perfil__isnull=True)
        self.stdout.write(f'👤 Usuarios sin perfil encontrados: {usuarios_sin_perfil.count()}')
        
        if not dry_run and usuarios_sin_perfil.exists():
            with transaction.atomic():
                for usuario in usuarios_sin_perfil:
                    PerfilUsuario.objects.create(
                        usuario=usuario,
                        numero_documento='',
                        telefono=''
                    )
                    self.stdout.write(f'✅ Perfil creado para {usuario.username}')
    
    def _eliminar_perfiles_duplicados(self, dry_run):
        """Elimina perfiles duplicados manteniendo solo el primero de cada usuario"""
        perfiles_duplicados = self._encontrar_perfiles_duplicados()
        usuarios_afectados = len(set(p.usuario for p in perfiles_duplicados))
        
        self.stdout.write(f'🔄 Usuarios con múltiples perfiles: {usuarios_afectados}')
        self.stdout.write(f'🗑️  Perfiles duplicados a eliminar: {len(perfiles_duplicados)}')
        
        if not dry_run and perfiles_duplicados:
            self._eliminar_perfiles(perfiles_duplicados)
    
    def _encontrar_perfiles_duplicados(self):
        """Encuentra todos los perfiles duplicados (mantiene el primero)"""
        perfiles_duplicados = []
        
        for usuario in User.objects.all():
            perfiles_usuario = PerfilUsuario.objects.filter(usuario=usuario)
            if perfiles_usuario.count() > 1:
                # Mantener solo el primero, eliminar el resto
                perfiles_duplicados.extend(list(perfiles_usuario[1:]))
        
        return perfiles_duplicados
    
    def _eliminar_perfiles(self, perfiles):
        """Elimina una lista de perfiles en una transacción atómica"""
        with transaction.atomic():
            for perfil in perfiles:
                usuario_nombre = perfil.usuario.username
                perfil.delete()
                self.stdout.write(f'🗑️  Perfil duplicado eliminado para {usuario_nombre}')
    
    def _eliminar_perfiles_huerfanos(self, dry_run):
        """Elimina perfiles sin usuario asociado"""
        perfiles_huerfanos = PerfilUsuario.objects.filter(usuario__isnull=True)
        
        if perfiles_huerfanos.exists():
            self.stdout.write(self.style.ERROR(
                f'\n🚨 PERFILES HUÉRFANOS ENCONTRADOS: {perfiles_huerfanos.count()}'
            ))
            if not dry_run:
                perfiles_huerfanos.delete()
                self.stdout.write('🗑️  Perfiles huérfanos eliminados')
    
    def _mostrar_estadisticas_finales(self, dry_run):
        """Muestra las estadísticas finales y el estado del sistema"""
        estadisticas = self._obtener_estadisticas()
        self._imprimir_estadisticas(estadisticas)
        self._verificar_integridad(estadisticas)
        self._mostrar_usuarios_sin_perfil()
        self._mostrar_mensaje_final(dry_run)
    
    def _obtener_estadisticas(self):
        """Obtiene las estadísticas actuales del sistema"""
        return {
            'total_usuarios': User.objects.count(),
            'total_perfiles': PerfilUsuario.objects.count(),
            'usuarios_con_perfil': User.objects.filter(perfil__isnull=False).count(),
        }
    
    def _imprimir_estadisticas(self, estadisticas):
        """Imprime las estadísticas del sistema"""
        self.stdout.write(self.style.SUCCESS('\n📊 ESTADÍSTICAS FINALES:'))
        self.stdout.write(f'👥 Total de usuarios: {estadisticas["total_usuarios"]}')
        self.stdout.write(f'📋 Total de perfiles: {estadisticas["total_perfiles"]}')
        self.stdout.write(f'✅ Usuarios con perfil: {estadisticas["usuarios_con_perfil"]}')
        self.stdout.write(
            f'❌ Usuarios sin perfil: '
            f'{estadisticas["total_usuarios"] - estadisticas["usuarios_con_perfil"]}'
        )
    
    def _verificar_integridad(self, estadisticas):
        """Verifica si hay integridad perfecta (1 usuario = 1 perfil)"""
        todos_iguales = (
            estadisticas['total_usuarios'] == 
            estadisticas['total_perfiles'] == 
            estadisticas['usuarios_con_perfil']
        )
        
        if todos_iguales:
            self.stdout.write(self.style.SUCCESS(
                '🎉 ¡Todos los usuarios tienen exactamente un perfil!'
            ))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Hay inconsistencias en los perfiles'))
    
    def _mostrar_usuarios_sin_perfil(self):
        """Muestra la lista de usuarios que no tienen perfil"""
        usuarios_sin_perfil = User.objects.filter(perfil__isnull=True)
        
        if usuarios_sin_perfil.exists():
            self.stdout.write(self.style.ERROR('\n❌ USUARIOS SIN PERFIL:'))
            for usuario in usuarios_sin_perfil:
                self.stdout.write(f'   - {usuario.username} (ID: {usuario.id})')
    
    def _mostrar_mensaje_final(self, dry_run):
        """Muestra el mensaje final según el modo de ejecución"""
        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n🔍 Ejecuta sin --dry-run para aplicar los cambios'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Limpieza completada!'))
        
        self.stdout.write('\n💡 Ahora puedes intentar crear usuarios desde el admin sin problemas')

