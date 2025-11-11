from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.utils import timezone
from core.admin_site import admin_site
from .models import PerfilUsuario
from .admin_forms import UsuarioCompletoAdminForm, PerfilUsuarioEditForm, UsuarioEditForm, PerfilUsuarioCompletoForm


# ===== CONSTANTES PARA STRINGS DUPLICADOS =====
# Estilos CSS reutilizables
MUTED_TEXT_STYLE = "color: #999;"
MUTED_SMALL_TEXT_STYLE = "color: #999; font-size: 0.8em;"

# Mensajes de estado reutilizables
MSG_SIN_PERFIL = f'<em style="{MUTED_TEXT_STYLE}">Sin perfil</em>'
MSG_SIN_DOCUMENTO = f'<em style="{MUTED_TEXT_STYLE}">Sin documento</em>'
MSG_SIN_TELEFONO = f'<em style="{MUTED_TEXT_STYLE}">Sin teléfono</em>'
MSG_SIN_UBICACION = f'<em style="{MUTED_TEXT_STYLE}">Sin ubicación</em>'
MSG_PROTEGIDO = f'<span style="{MUTED_SMALL_TEXT_STYLE}">🔒 Protegido</span>'

# Estilos para enlaces y botones
LINK_STYLE = "color: #007cba;"
BUTTON_DELETE_STYLE = "background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 0.8em;"
WARNING_TEXT_STYLE = "color: #dc3545; font-size: 0.7em;"

# Constante para el título de la sección de identificación
IDENT_SECTION_TITLE = '🆔 Identificación'
# Constante para el título de la sección de información personal
PERSONAL_SECTION_TITLE = '👤 Información Personal'

class PerfilUsuarioInline(admin.StackedInline):
    """Inline simplificado para mostrar el perfil en la página de usuario"""
    model = PerfilUsuario
    form = PerfilUsuarioEditForm
    can_delete = False
    verbose_name = "📋 Perfil Completo del Usuario"
    verbose_name_plural = "📋 Perfiles de Usuario"
    max_num = 1  # Solo un perfil por usuario
    min_num = 0  # No requerir perfil inicialmente (se crea automáticamente)
    extra = 0    # No mostrar formularios extra vacíos
    
    fieldsets = (
        (IDENT_SECTION_TITLE, {
            'fields': ('tipo_documento', 'numero_documento'),
            'description': 'Información de identificación oficial del usuario'
        }),
        ('📱 Contacto', {
            'fields': ('telefono', 'direccion', 'ciudad', 'departamento', 'codigo_postal'),
            'description': 'Información de contacto y ubicación'
        }),
        (PERSONAL_SECTION_TITLE, {
            'fields': ('fecha_nacimiento', 'genero', 'estado_civil'),
            'classes': ('collapse',),
            'description': 'Información personal opcional'
        }),
        ('💼 Información Profesional', {
            'fields': ('profesion', 'empresa', 'cargo'),
            'classes': ('collapse',),
            'description': 'Información laboral y profesional'
        }),
        ('⚙️ Configuración', {
            'fields': ('activo',),
            'classes': ('collapse',),
            'description': 'Configuración del perfil'
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura dinámicos"""
        readonly = []
        
        # Si el perfil ya existe y tiene datos críticos, protegerlos
        if obj and hasattr(obj, 'perfil'):
            perfil = obj.perfil
            if perfil.numero_documento:
                # No permitir cambiar documento si ya está establecido
                # (para evitar problemas de integridad)
                pass  # Permitir cambio por ahora, pero se puede restringir
        
        return readonly


class UsuarioPersonalizadoAdmin(UserAdmin):
    """Admin personalizado para Usuario con perfil integrado"""
    inlines = (PerfilUsuarioInline,)
    
    # Usar formularios personalizados
    add_form = UsuarioCompletoAdminForm
    form = UsuarioEditForm
    
    list_display = (
        'get_avatar', 'username', 'get_nombre_completo', 'email', 
        'get_documento', 'get_telefono', 'get_ciudad', 'get_status', 
        'get_tipo_usuario', 'get_acciones', 'date_joined'
    )
    
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 'date_joined',
        'perfil__tipo_documento', 'perfil__ciudad', 'perfil__departamento',
        'perfil__genero', 'perfil__acepta_terminos'
    )
    
    search_fields = (
        'username', 'first_name', 'last_name', 'email',
        'perfil__numero_documento', 'perfil__telefono', 'perfil__ciudad'
    )
    
    list_per_page = 25
    
    # Fieldsets para creación de usuarios (formulario unificado)
    add_fieldsets = (
        ('🔐 Credenciales de Acceso', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
            'description': 'Información básica para el acceso al sistema'
        }),
        (PERSONAL_SECTION_TITLE, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email'),
            'description': 'Datos personales del usuario'
        }),
        (IDENT_SECTION_TITLE, {
            'classes': ('wide',),
            'fields': ('tipo_documento', 'numero_documento', 'telefono'),
            'description': 'Información de identificación y contacto'
        }),
        ('📍 Ubicación', {
            'classes': ('wide', 'collapse'),
            'fields': ('ciudad', 'departamento'),
            'description': 'Información de ubicación (opcional)'
        }),
        ('👥 Información Adicional', {
            'classes': ('wide', 'collapse'),
            'fields': ('fecha_nacimiento', 'genero', 'profesion'),
            'description': 'Información complementaria (opcional)'
        }),
        ('⚙️ Permisos del Sistema', {
            'classes': ('wide', 'collapse'),
            'fields': ('is_active', 'is_staff'),
            'description': 'Configuración de acceso y permisos'
        }),
    )
    
    # Fieldsets para edición de usuarios existentes
    fieldsets = (
        ('🔐 Información de Acceso', {
            'fields': ('username', 'password')
        }),
        (PERSONAL_SECTION_TITLE, {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('🔑 Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('📅 Fechas Importantes', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    def get_avatar(self, obj):
        """Mostrar avatar del usuario"""
        if obj.is_superuser:
            return "👑"
        elif obj.is_staff:
            return "👨‍💼"
        elif obj.is_active:
            return "👤"
        else:
            return "❌"
    get_avatar.short_description = ""
    
    def get_nombre_completo(self, obj):
        """Mostrar nombre completo del usuario"""
        nombre = f"{obj.first_name} {obj.last_name}".strip()
        if nombre:
            return format_html('<strong>{}</strong>', nombre)
        return format_html('<em>{}</em>', obj.username)
    get_nombre_completo.short_description = "👤 Nombre Completo"
    get_nombre_completo.admin_order_field = 'first_name'
    
    def get_documento(self, obj):
        """Mostrar documento en la lista"""
        try:
            if hasattr(obj, 'perfil') and obj.perfil.numero_documento:
                return format_html(
                    '<span title="{}">{}</span>',
                    obj.perfil.documento_completo,
                    obj.perfil.numero_documento
                )
            return format_html(MSG_SIN_DOCUMENTO)
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return format_html(MSG_SIN_PERFIL)
    get_documento.short_description = "🆔 Documento"
    get_documento.admin_order_field = 'perfil__numero_documento'
    
    def get_telefono(self, obj):
        """Mostrar teléfono en la lista"""
        try:
            if hasattr(obj, 'perfil') and obj.perfil.telefono:
                return format_html(
                    '<a href="tel:{}" style="{}">{}</a>',
                    obj.perfil.telefono,
                    LINK_STYLE,
                    obj.perfil.telefono
                )
            return format_html(MSG_SIN_TELEFONO)
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return format_html(MSG_SIN_PERFIL)
    get_telefono.short_description = "📱 Teléfono"
    get_telefono.admin_order_field = 'perfil__telefono'
    
    def get_ciudad(self, obj):
        """Mostrar ciudad del usuario"""
        try:
            if hasattr(obj, 'perfil') and obj.perfil.ciudad:
                return format_html(
                    '<span title="{}, {}">{}</span>',
                    obj.perfil.ciudad,
                    obj.perfil.departamento or 'Colombia',
                    obj.perfil.ciudad
                )
            return format_html(MSG_SIN_UBICACION)
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return format_html(MSG_SIN_PERFIL)
    get_ciudad.short_description = "📍 Ciudad"
    get_ciudad.admin_order_field = 'perfil__ciudad'
    
    def get_status(self, obj):
        """Mostrar estado del usuario"""
        if obj.is_active:
            return format_html('<span style="color: green;">✅ Activo</span>')
        else:
            return format_html('<span style="color: red;">❌ Inactivo</span>')
    get_status.short_description = "📊 Estado"
    get_status.admin_order_field = 'is_active'
    
    def get_tipo_usuario(self, obj):
        """Mostrar tipo de usuario"""
        if obj.is_superuser:
            return format_html('<span style="color: #d63384;">👑 Super</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #fd7e14;">👨‍💼 Staff</span>')
        else:
            return format_html('<span style="color: #6c757d;">👤 Usuario</span>')
    get_tipo_usuario.short_description = "🏷️ Tipo"
    get_tipo_usuario.admin_order_field = 'is_superuser'
    
    def get_acciones(self, obj):
        """Mostrar botones de acción"""
        if obj.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
            # No permitir eliminar el último superusuario
            return format_html(MSG_PROTEGIDO)
        
        # Verificar relaciones
        tiene_relaciones = False
        relaciones_info = []
        
        try:
            if hasattr(obj, 'perfil'):
                relaciones_info.append("Perfil")
                tiene_relaciones = True
        except (AttributeError, PerfilUsuario.DoesNotExist):
            pass
        
        # Contar otros objetos relacionados si existen
        # Aquí puedes agregar más verificaciones según tus modelos futuros
        
        if tiene_relaciones:
            return format_html(
                '<a href="#" onclick="eliminarUsuarioConRelaciones({}, \'{}\', [{}]); return false;" '
                'style="{} margin-right: 5px;">'
                '🗑️ Eliminar</a>'
                '<span style="{}">⚠️ Tiene relaciones</span>',
                obj.id,
                obj.username,
                ', '.join([f'"{r}"' for r in relaciones_info]),
                BUTTON_DELETE_STYLE,
                WARNING_TEXT_STYLE
            )
        else:
            return format_html(
                '<a href="#" onclick="eliminarUsuarioSimple({}, \'{}\'); return false;" '
                'style="{}">'
                '🗑️ Eliminar</a>',
                obj.id,
                obj.username,
                BUTTON_DELETE_STYLE
            )
    get_acciones.short_description = "🔧 Acciones"
    
    def get_urls(self):
        """Agregar URLs personalizadas"""
        urls = super().get_urls()
        custom_urls = [
            path('eliminar-usuario/<int:user_id>/', 
                 self.admin_site.admin_view(self.eliminar_usuario_view), 
                 name='eliminar_usuario'),
        ]
        return custom_urls + urls
    
    def eliminar_usuario_view(self, request, user_id):
        """Vista para eliminar usuario con validaciones"""
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        try:
            user = User.objects.get(id=user_id)
            
            # Validaciones de seguridad
            if user.is_superuser and User.objects.filter(is_superuser=True).count() <= 1:
                return JsonResponse({
                    'error': 'No se puede eliminar el último superusuario del sistema'
                }, status=400)
            
            if user == request.user:
                return JsonResponse({
                    'error': 'No puedes eliminarte a ti mismo'
                }, status=400)
            
            # Información de relaciones
            relaciones = []
            
            with transaction.atomic():
                # Eliminar perfil si existe
                try:
                    if hasattr(user, 'perfil'):
                        user.perfil.delete()
                        relaciones.append('Perfil de usuario')
                except (AttributeError, PerfilUsuario.DoesNotExist):
                    pass
                
                # Aquí puedes agregar más eliminaciones de objetos relacionados
                # según tus modelos futuros
                
                # Eliminar usuario
                username = user.username
                user.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Usuario "{username}" eliminado exitosamente',
                'relaciones_eliminadas': relaciones
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'Usuario no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Error al eliminar usuario: {str(e)}'}, status=500)


@admin.register(PerfilUsuario, site=admin_site)
@admin.register(PerfilUsuario)  # También en admin por defecto
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Admin inteligente para gestión directa de perfiles con creación automática de usuarios"""
    form = PerfilUsuarioCompletoForm
    
    list_display = (
        'usuario', 'documento_completo', 'telefono', 
        'ciudad', 'activo', 'fecha_creacion'
    )
    
    list_filter = (
        'tipo_documento', 'genero', 'estado_civil', 'ciudad', 
        'departamento', 'activo', 'acepta_terminos'
    )
    
    search_fields = (
        'usuario__username', 'usuario__first_name', 'usuario__last_name',
        'numero_documento', 'telefono', 'ciudad'
    )
    
    def get_fieldsets(self, request, obj=None):
        """Fieldsets dinámicos según si es creación o edición"""
        if obj:  # Editando perfil existente
            return (
                ('👤 Usuario Asociado', {
                    'fields': ('usuario',),
                    'description': 'Usuario asociado a este perfil (no se puede cambiar)'
                }),
                (IDENT_SECTION_TITLE, {
                    'fields': ('tipo_documento', 'numero_documento'),
                    'description': 'Información de identificación oficial'
                }),
                ('📱 Contacto', {
                    'fields': ('telefono', 'direccion', 'ciudad', 'departamento', 'codigo_postal'),
                    'description': 'Información de contacto y ubicación'
                }),
                ('👥 Información Personal', {
                    'fields': ('fecha_nacimiento', 'genero', 'estado_civil'),
                    'classes': ('collapse',),
                    'description': 'Información personal opcional'
                }),
                ('💼 Información Profesional', {
                    'fields': ('profesion', 'empresa', 'cargo'),
                    'classes': ('collapse',),
                    'description': 'Información laboral y profesional'
                }),
                ('⚙️ Configuración', {
                    'fields': ('activo',),
                    'classes': ('collapse',),
                    'description': 'Configuración del perfil'
                }),
                ('📅 Metadatos', {
                    'fields': ('fecha_creacion', 'fecha_actualizacion'),
                    'classes': ('collapse',),
                    'description': 'Información del sistema'
                }),
            )
        else:  # Creando nuevo perfil
            return (
                ('✨ Creación Inteligente', {
                    'fields': ('crear_usuario_automaticamente',),
                    'description': 'Marque esta opción para crear automáticamente un usuario con los datos del perfil'
                }),
                ('👤 Usuario Existente', {
                    'fields': ('usuario',),
                    'description': 'Seleccione un usuario existente (solo si NO marcó "Crear automáticamente")'
                }),
                ('🔐 Datos del Nuevo Usuario', {
                    'fields': ('username', 'first_name', 'last_name', 'email', 'password', 'is_active'),
                    'classes': ('collapse',),
                    'description': 'Complete estos datos para crear un nuevo usuario (se generarán automáticamente si se dejan vacíos)'
                }),
                (IDENT_SECTION_TITLE, {
                    'fields': ('tipo_documento', 'numero_documento'),
                    'description': 'Información de identificación oficial (requerida)'
                }),
                ('📱 Contacto', {
                    'fields': ('telefono', 'direccion', 'ciudad', 'departamento', 'codigo_postal'),
                    'description': 'Información de contacto y ubicación'
                }),
                ('👥 Información Personal', {
                    'fields': ('fecha_nacimiento', 'genero', 'estado_civil'),
                    'classes': ('collapse',),
                    'description': 'Información personal opcional'
                }),
                ('💼 Información Profesional', {
                    'fields': ('profesion', 'empresa', 'cargo'),
                    'classes': ('collapse',),
                    'description': 'Información laboral y profesional'
                }),
                ('⚙️ Configuración', {
                    'fields': ('activo',),
                    'classes': ('collapse',),
                    'description': 'Configuración del perfil'
                }),
            )
    
    def get_readonly_fields(self, request, obj=None):
        """Campos de solo lectura dinámicos"""
        readonly = ['fecha_creacion', 'fecha_actualizacion']
        
        # Si estamos editando un perfil existente
        if obj and obj.pk:
            # El usuario asociado no se puede cambiar al editar
            readonly.append('usuario')
        
        return readonly
    
    def save_model(self, request, obj, form, change):
        """Personalizar el guardado del modelo"""
        # Mostrar mensaje informativo sobre lo que se creó
        if not change:  # Solo para nuevos objetos
            crear_automatico = form.cleaned_data.get('crear_usuario_automaticamente')
            if crear_automatico:
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                
                # Guardar el objeto
                super().save_model(request, obj, form, change)
                
                # Mostrar mensaje con credenciales
                messages.success(request, format_html(
                    '✅ <strong>Usuario y perfil creados exitosamente!</strong><br>'
                    '👤 <strong>Usuario:</strong> {}<br>'
                    '🔑 <strong>Contraseña:</strong> {} <br>'
                    '📧 <strong>Email:</strong> {}<br>'
                    '💡 <em>Guarde estas credenciales ya que la contraseña no se mostrará nuevamente.</em>',
                    username, password, form.cleaned_data.get('email')
                ))
            else:
                super().save_model(request, obj, form, change)
                messages.success(request, '✅ Perfil asociado al usuario existente correctamente.')
        else:
            super().save_model(request, obj, form, change)
    
    class Media:
        """Agregar JavaScript personalizado"""
        js = ('admin/js/perfil_usuario_inteligente.js',)


@admin.register(Session, site=admin_site)
@admin.register(Session)  # También en admin por defecto
class SessionAdmin(admin.ModelAdmin):
    """Admin para gestión de sesiones activas"""
    list_display = ('session_key_short', 'get_user', 'expire_date', 'is_expired')
    list_filter = ('expire_date',)
    search_fields = ('session_key',)
    readonly_fields = ('session_key', 'session_data', 'expire_date')
    
    def session_key_short(self, obj):
        """Mostrar versión corta de la session key"""
        return f"{obj.session_key[:8]}..."
    session_key_short.short_description = "🔑 Session Key"
    
    def get_user(self, obj):
        """Obtener usuario de la sesión"""
        try:
            from django.contrib.sessions.backends.db import SessionStore
            store = SessionStore(session_key=obj.session_key)
            user_id = store.get('_auth_user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    return format_html(
                        '<a href="/admin/auth/user/{}/change/">{}</a>',
                        user.id,
                        user.username
                    )
                except User.DoesNotExist:
                    return format_html('<em style="color: #999;">Usuario eliminado</em>')
            return format_html('<em style="color: #999;">Sesión anónima</em>')
        except Exception:
            return format_html('<em style="color: #999;">Error al obtener usuario</em>')
    get_user.short_description = "👤 Usuario"
    
    def is_expired(self, obj):
        """Verificar si la sesión está expirada"""
        now = timezone.now()
        if obj.expire_date < now:
            return format_html('<span style="color: red;">❌ Expirada</span>')
        else:
            return format_html('<span style="color: green;">✅ Activa</span>')
    is_expired.short_description = "📊 Estado"
    
    def has_add_permission(self, request):
        """No permitir crear sesiones manualmente"""
        _ = request  # Marcar como intencionalmente no usado
        return False


@admin.register(ContentType, site=admin_site)
@admin.register(ContentType)  # También en admin por defecto
class ContentTypeAdmin(admin.ModelAdmin):
    """Admin para gestión de tipos de contenido"""
    list_display = ('app_label', 'model', 'name', 'id')
    list_filter = ('app_label',)
    search_fields = ('app_label', 'model', 'name')
    readonly_fields = ('app_label', 'model', 'name')
    
    def has_add_permission(self, request):
        """No permitir crear content types manualmente"""
        _ = request  # Marcar como intencionalmente no usado
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar content types"""
        _ = request, obj  # Marcar como intencionalmente no usados
        return False


# Registrar en el admin site personalizado
# NOTA: User y Group se registran en core/admin.py para mantener el código organizado

# También mantener el registro en el admin site por defecto para compatibilidad
admin.site.unregister(User)
admin.site.register(User, UsuarioPersonalizadoAdmin)

# Personalizar títulos del admin por defecto (por si se accede directamente)
admin.site.site_header = "🏢 S_CONTABLE - Panel de Administración"
admin.site.site_title = "S_CONTABLE Admin"
admin.site.index_title = "🇨🇴 Sistema Contable Colombiano - Panel de Control"

# Contexto personalizado para el admin
def admin_context():
    """Agregar estadísticas al contexto del admin"""
    context = {}
    try:
        context.update({
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_profiles': PerfilUsuario.objects.count(),
            'admin_users': User.objects.filter(is_superuser=True).count(),
        })
    except (AttributeError, ImportError):
        # Manejo específico de errores de atributos e importación
        context.update({
            'total_users': 0,
            'active_users': 0,
            'total_profiles': 0,
            'admin_users': 0,
        })
    return context

# Registrar el contexto
from django.template import Library
register = Library()

@register.inclusion_tag('admin/index.html', takes_context=True)
def admin_stats(context):
    """Template tag para mostrar estadísticas"""
    # El contexto se puede usar para futuras extensiones si es necesario
    return admin_context()
