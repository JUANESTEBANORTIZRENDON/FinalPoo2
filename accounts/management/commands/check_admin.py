from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.admin import site
from django.utils import timezone


class Command(BaseCommand):
    help = 'Verificar el estado del panel de administración'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando estado del panel de administración...'))
        
        # Verificar usuarios administradores
        superusers = User.objects.filter(is_superuser=True)
        staff_users = User.objects.filter(is_staff=True)
        
        self.stdout.write(f'👑 Superusuarios: {superusers.count()}')
        for user in superusers:
            status = "✅ Activo" if user.is_active else "❌ Inactivo"
            self.stdout.write(f'   - {user.username} ({user.email}) - {status}')
        
        self.stdout.write(f'👨‍💼 Staff users: {staff_users.count()}')
        for user in staff_users:
            if not user.is_superuser:
                status = "✅ Activo" if user.is_active else "❌ Inactivo"
                self.stdout.write(f'   - {user.username} ({user.email}) - {status}')
        
        # Verificar sesiones activas
        active_sessions = Session.objects.filter(expire_date__gt=timezone.now())
        expired_sessions = Session.objects.filter(expire_date__lte=timezone.now())
        
        self.stdout.write(f'🔑 Sesiones activas: {active_sessions.count()}')
        self.stdout.write(f'⏰ Sesiones expiradas: {expired_sessions.count()}')
        
        # Verificar modelos registrados en admin
        registered_models = site._registry
        self.stdout.write(f'📊 Modelos registrados en admin: {len(registered_models)}')
        
        # Verificar modelos críticos
        from django.contrib.contenttypes.models import ContentType
        
        if Session in registered_models:
            self.stdout.write(self.style.SUCCESS('✅ Modelo Session registrado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Modelo Session NO registrado'))
            
        if ContentType in registered_models:
            self.stdout.write(self.style.SUCCESS('✅ Modelo ContentType registrado correctamente'))
        else:
            self.stdout.write(self.style.ERROR('❌ Modelo ContentType NO registrado'))
        
        # Verificar URLs del admin
        from django.urls import reverse
        try:
            admin_url = reverse('admin:index')
            sessions_url = reverse('admin:sessions_session_changelist')
            contenttypes_url = reverse('admin:contenttypes_contenttype_changelist')
            self.stdout.write(self.style.SUCCESS(f'✅ URLs del admin funcionando:'))
            self.stdout.write(f'   - Admin index: {admin_url}')
            self.stdout.write(f'   - Sessions list: {sessions_url}')
            self.stdout.write(f'   - ContentTypes list: {contenttypes_url}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en URLs: {e}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Verificación completada'))
