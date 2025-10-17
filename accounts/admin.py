from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from .models import PerfilUsuario


class PerfilUsuarioInline(admin.StackedInline):
    """Inline para mostrar el perfil en la página de usuario"""
    model = PerfilUsuario
    can_delete = False
    verbose_name = "Perfil de Usuario"
    verbose_name_plural = "Perfiles de Usuario"
    
    fieldsets = (
        ('Información Personal', {
            'fields': (
                'tipo_documento', 'numero_documento', 'telefono', 
                'fecha_nacimiento', 'genero', 'estado_civil'
            )
        }),
        ('Información de Contacto', {
            'fields': (
                'direccion', 'ciudad', 'departamento', 'pais', 'codigo_postal'
            )
        }),
        ('Información Profesional', {
            'fields': ('profesion', 'empresa', 'cargo')
        }),
        ('Configuración del Sistema', {
            'fields': (
                'acepta_terminos', 'acepta_politica_privacidad', 
                'recibir_notificaciones', 'activo'
            )
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')


class UsuarioPersonalizadoAdmin(UserAdmin):
    """Admin personalizado para Usuario con perfil integrado"""
    inlines = (PerfilUsuarioInline,)
    
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
            return format_html('<em style="color: #999;">Sin documento</em>')
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return format_html('<em style="color: #999;">Sin perfil</em>')
    get_documento.short_description = "🆔 Documento"
    get_documento.admin_order_field = 'perfil__numero_documento'
    
    def get_telefono(self, obj):
        """Mostrar teléfono en la lista"""
        try:
            if hasattr(obj, 'perfil') and obj.perfil.telefono:
                return format_html(
                    '<a href="tel:{}" style="color: #007cba;">{}</a>',
                    obj.perfil.telefono,
                    obj.perfil.telefono
                )
            return format_html('<em style="color: #999;">Sin teléfono</em>')
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return format_html('<em style="color: #999;">Sin perfil</em>')
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
            return format_html('<em style="color: #999;">Sin ubicación</em>')
        except (AttributeError, PerfilUsuario.DoesNotExist):
            return format_html('<em style="color: #999;">Sin perfil</em>')
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
            return format_html(
                '<span style="color: #999; font-size: 0.8em;">🔒 Protegido</span>'
            )
        
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
                'style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; '
                'text-decoration: none; font-size: 0.8em; margin-right: 5px;">'
                '🗑️ Eliminar</a>'
                '<span style="color: #dc3545; font-size: 0.7em;">⚠️ Tiene relaciones</span>',
                obj.id,
                obj.username,
                ', '.join([f'"{r}"' for r in relaciones_info])
            )
        else:
            return format_html(
                '<a href="#" onclick="eliminarUsuarioSimple({}, \'{}\'); return false;" '
                'style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; '
                'text-decoration: none; font-size: 0.8em;">'
                '🗑️ Eliminar</a>',
                obj.id,
                obj.username
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


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Admin para gestión directa de perfiles"""
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
    
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Usuario', {
            'fields': ('usuario',)
        }),
        ('Información Personal', {
            'fields': (
                'tipo_documento', 'numero_documento', 'telefono', 
                'fecha_nacimiento', 'genero', 'estado_civil'
            )
        }),
        ('Información de Contacto', {
            'fields': (
                'direccion', 'ciudad', 'departamento', 'pais', 'codigo_postal'
            )
        }),
        ('Información Profesional', {
            'fields': ('profesion', 'empresa', 'cargo')
        }),
        ('Configuración del Sistema', {
            'fields': (
                'acepta_terminos', 'acepta_politica_privacidad', 
                'recibir_notificaciones', 'activo'
            )
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )


# Desregistrar el admin por defecto y registrar el personalizado
admin.site.unregister(User)
admin.site.register(User, UsuarioPersonalizadoAdmin)

# Personalizar títulos del admin
admin.site.site_header = "🏢 S_CONTABLE - Panel de Administración"
admin.site.site_title = "S_CONTABLE Admin"
admin.site.index_title = "🇨🇴 Sistema Contable Colombiano - Panel de Control"

# Contexto personalizado para el admin
def admin_context(request):
    """Agregar estadísticas al contexto del admin"""
    context = {}
    try:
        context.update({
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_profiles': PerfilUsuario.objects.count(),
            'admin_users': User.objects.filter(is_superuser=True).count(),
        })
    except (AttributeError, ImportError, Exception) as e:
        # Log del error para debugging si es necesario
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
    request = context['request']
    return admin_context(request)
