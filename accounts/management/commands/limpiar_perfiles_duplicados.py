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
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 MODO DRY-RUN: Solo mostrando qué se haría...'))
        else:
            self.stdout.write(self.style.SUCCESS('🧹 Iniciando limpieza de perfiles...'))
        
        # 1. Buscar usuarios sin perfil
        usuarios_sin_perfil = User.objects.filter(perfil__isnull=True)
        
        self.stdout.write(f'👤 Usuarios sin perfil encontrados: {usuarios_sin_perfil.count()}')
        
        if not dry_run and usuarios_sin_perfil.exists():
            with transaction.atomic():
                for usuario in usuarios_sin_perfil:
                    perfil = PerfilUsuario.objects.create(
                        usuario=usuario,
                        numero_documento='',
                        telefono=''
                    )
                    self.stdout.write(f'✅ Perfil creado para {usuario.username}')
        
        # 2. Buscar perfiles duplicados (aunque no debería haber con OneToOne)
        perfiles_duplicados = []
        usuarios_con_multiples_perfiles = []
        
        for usuario in User.objects.all():
            perfiles_usuario = PerfilUsuario.objects.filter(usuario=usuario)
            if perfiles_usuario.count() > 1:
                usuarios_con_multiples_perfiles.append(usuario)
                perfiles_duplicados.extend(list(perfiles_usuario[1:]))  # Mantener solo el primero
        
        self.stdout.write(f'🔄 Usuarios con múltiples perfiles: {len(usuarios_con_multiples_perfiles)}')
        self.stdout.write(f'🗑️  Perfiles duplicados a eliminar: {len(perfiles_duplicados)}')
        
        if not dry_run and perfiles_duplicados:
            with transaction.atomic():
                for perfil in perfiles_duplicados:
                    usuario_nombre = perfil.usuario.username
                    perfil.delete()
                    self.stdout.write(f'🗑️  Perfil duplicado eliminado para {usuario_nombre}')
        
        # 3. Verificar integridad final
        total_usuarios = User.objects.count()
        total_perfiles = PerfilUsuario.objects.count()
        usuarios_con_perfil = User.objects.filter(perfil__isnull=False).count()
        
        self.stdout.write(self.style.SUCCESS('\n📊 ESTADÍSTICAS FINALES:'))
        self.stdout.write(f'👥 Total de usuarios: {total_usuarios}')
        self.stdout.write(f'📋 Total de perfiles: {total_perfiles}')
        self.stdout.write(f'✅ Usuarios con perfil: {usuarios_con_perfil}')
        self.stdout.write(f'❌ Usuarios sin perfil: {total_usuarios - usuarios_con_perfil}')
        
        if total_usuarios == total_perfiles == usuarios_con_perfil:
            self.stdout.write(self.style.SUCCESS('🎉 ¡Todos los usuarios tienen exactamente un perfil!'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Hay inconsistencias en los perfiles'))
        
        # 4. Mostrar usuarios problemáticos si los hay
        usuarios_sin_perfil_final = User.objects.filter(perfil__isnull=True)
        if usuarios_sin_perfil_final.exists():
            self.stdout.write(self.style.ERROR('\n❌ USUARIOS SIN PERFIL:'))
            for usuario in usuarios_sin_perfil_final:
                self.stdout.write(f'   - {usuario.username} (ID: {usuario.id})')
        
        # 5. Verificar perfiles huérfanos
        perfiles_huerfanos = PerfilUsuario.objects.filter(usuario__isnull=True)
        if perfiles_huerfanos.exists():
            self.stdout.write(self.style.ERROR(f'\n🚨 PERFILES HUÉRFANOS ENCONTRADOS: {perfiles_huerfanos.count()}'))
            if not dry_run:
                perfiles_huerfanos.delete()
                self.stdout.write('🗑️  Perfiles huérfanos eliminados')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 Ejecuta sin --dry-run para aplicar los cambios'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Limpieza completada!'))
            
        self.stdout.write('\n💡 Ahora puedes intentar crear usuarios desde el admin sin problemas')
