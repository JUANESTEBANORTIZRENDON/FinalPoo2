from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from core.admin_site import contable_admin_site
from .models import Empresa, PerfilEmpresa, EmpresaActiva, HistorialCambios

@admin.register(Empresa, site=contable_admin_site)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'nit', 'email', 'telefono', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion', 'ciudad')
    search_fields = ('razon_social', 'nit', 'email')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('razon_social', 'nit', 'nombre_comercial')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'direccion', 'ciudad')
        }),
        ('Propietario', {
            'fields': ('propietario',)
        }),
        ('Estado', {
            'fields': ('activa',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PerfilEmpresa, site=contable_admin_site)
class PerfilEmpresaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'rol', 'activo', 'fecha_asignacion')
    list_filter = ('rol', 'activo', 'fecha_asignacion')
    search_fields = ('usuario__username', 'usuario__email', 'empresa__razon_social')
    readonly_fields = ('fecha_asignacion',)
    
    fieldsets = (
        ('Asignación', {
            'fields': ('usuario', 'empresa', 'rol')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion',),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmpresaActiva, site=contable_admin_site)
class EmpresaActivaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'empresa', 'fecha_seleccion')
    list_filter = ('fecha_seleccion',)
    search_fields = ('usuario__username', 'empresa__razon_social')
    readonly_fields = ('fecha_seleccion',)


@admin.register(HistorialCambios, site=contable_admin_site)
class HistorialCambiosAdmin(admin.ModelAdmin):
    list_display = (
        'icono_accion_display', 
        'usuario_display', 
        'empresa_display', 
        'tipo_accion_display',
        'descripcion_corta', 
        'fecha_hora_display',
        'exitosa_display',
        'duracion_display'
    )
    list_filter = (
        'tipo_accion', 
        'exitosa', 
        'fecha_hora',
        ('empresa', admin.RelatedOnlyFieldListFilter),
        ('usuario', admin.RelatedOnlyFieldListFilter)
    )
    search_fields = (
        'usuario__username', 
        'usuario__first_name', 
        'usuario__last_name',
        'empresa__razon_social', 
        'descripcion',
        'ip_address'
    )
    readonly_fields = (
        'usuario', 'empresa', 'tipo_accion', 'descripcion', 
        'modelo_afectado', 'objeto_id', 'datos_anteriores', 'datos_nuevos',
        'ip_address', 'user_agent', 'url_solicitada', 'metodo_http',
        'fecha_hora', 'duracion_ms', 'exitosa', 'mensaje_error'
    )
    
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
    list_per_page = 50
    list_max_show_all = 200
    
    fieldsets = (
        ('👤 Información del Usuario', {
            'fields': ('usuario', 'empresa')
        }),
        ('⚡ Acción Realizada', {
            'fields': ('tipo_accion', 'descripcion', 'fecha_hora')
        }),
        ('🔧 Información Técnica', {
            'fields': ('modelo_afectado', 'objeto_id', 'exitosa', 'duracion_ms', 'mensaje_error'),
            'classes': ('collapse',)
        }),
        ('🌐 Contexto Web', {
            'fields': ('ip_address', 'user_agent', 'url_solicitada', 'metodo_http'),
            'classes': ('collapse',)
        }),
        ('📊 Datos del Cambio', {
            'fields': ('datos_anteriores_display', 'datos_nuevos_display'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        # Todos los campos son de solo lectura ya que es un log de auditoría
        return self.readonly_fields
    
    def has_add_permission(self, request):
        # No permitir agregar registros manualmente
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Solo superusuarios pueden eliminar registros de auditoría
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # No permitir editar registros de auditoría
        return False
    
    def icono_accion_display(self, obj):
        """Muestra el icono de la acción"""
        return format_html(
            '<span style="font-size: 1.2em;" title="{}">{}</span>',
            obj.get_tipo_accion_display(),
            obj.icono_accion
        )
    icono_accion_display.short_description = '🎯'
    icono_accion_display.admin_order_field = 'tipo_accion'
    
    def usuario_display(self, obj):
        """Muestra información del usuario con avatar"""
        nombre = obj.usuario.get_full_name() or obj.usuario.username
        inicial = obj.usuario.first_name[0] if obj.usuario.first_name else obj.usuario.username[0]
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 24px; height: 24px; border-radius: 50%; '
            'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); '
            'display: flex; align-items: center; justify-content: center; '
            'color: white; font-weight: 600; font-size: 0.7rem;">{}</div>'
            '<div>'
            '<div style="font-weight: 500;">{}</div>'
            '<small style="color: #6c757d;">{}</small>'
            '</div>'
            '</div>',
            inicial.upper(),
            nombre,
            obj.rol_usuario
        )
    usuario_display.short_description = '👤 Usuario'
    usuario_display.admin_order_field = 'usuario__username'
    
    def empresa_display(self, obj):
        """Muestra información de la empresa"""
        if obj.empresa:
            return format_html(
                '<div>'
                '<div style="font-weight: 500;">🏢 {}</div>'
                '<small style="color: #6c757d;">NIT: {}</small>'
                '</div>',
                obj.empresa.razon_social,
                obj.empresa.nit
            )
        return format_html('<span style="color: #6c757d;">Sin empresa</span>')
    empresa_display.short_description = '🏢 Empresa'
    empresa_display.admin_order_field = 'empresa__razon_social'
    
    def tipo_accion_display(self, obj):
        """Muestra el tipo de acción con color"""
        colores = {
            'usuario_login': '#28a745',
            'usuario_logout': '#6c757d',
            'empresa_crear': '#007bff',
            'empresa_editar': '#ffc107',
            'factura_crear': '#17a2b8',
            'error_sistema': '#dc3545',
            'acceso_denegado': '#dc3545',
        }
        color = colores.get(obj.tipo_accion, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-weight: 500;">{}</span>',
            color,
            obj.get_tipo_accion_display()
        )
    tipo_accion_display.short_description = '⚡ Tipo de Acción'
    tipo_accion_display.admin_order_field = 'tipo_accion'
    
    def descripcion_corta(self, obj):
        """Muestra una descripción truncada"""
        if len(obj.descripcion) > 60:
            return format_html(
                '<span title="{}">{}</span>',
                obj.descripcion,
                obj.descripcion[:60] + '...'
            )
        return obj.descripcion
    descripcion_corta.short_description = '📝 Descripción'
    descripcion_corta.admin_order_field = 'descripcion'
    
    def fecha_hora_display(self, obj):
        """Muestra fecha y hora formateada"""
        return format_html(
            '<div>'
            '<div style="font-weight: 500;">{}</div>'
            '<small style="color: #6c757d;">{}</small>'
            '</div>',
            obj.fecha_hora.strftime('%d/%m/%Y'),
            obj.fecha_hora.strftime('%H:%M:%S')
        )
    fecha_hora_display.short_description = '🕐 Fecha y Hora'
    fecha_hora_display.admin_order_field = 'fecha_hora'
    
    def exitosa_display(self, obj):
        """Muestra el estado de la acción"""
        if obj.exitosa:
            return format_html(
                '<span style="color: #28a745; font-weight: 500;">✅ Exitosa</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: 500;" title="{}">❌ Error</span>',
                obj.mensaje_error or 'Error desconocido'
            )
    exitosa_display.short_description = '✅ Estado'
    exitosa_display.admin_order_field = 'exitosa'
    
    def duracion_display(self, obj):
        """Muestra la duración de la acción"""
        if obj.duracion_ms:
            if obj.duracion_ms < 1000:
                return format_html('<span style="color: #28a745;">{} ms</span>', obj.duracion_ms)
            elif obj.duracion_ms < 5000:
                return format_html('<span style="color: #ffc107;">{} ms</span>', obj.duracion_ms)
            else:
                return format_html('<span style="color: #dc3545;">{} ms</span>', obj.duracion_ms)
        return '-'
    duracion_display.short_description = '⏱️ Duración'
    duracion_display.admin_order_field = 'duracion_ms'
    
    def datos_anteriores_display(self, obj):
        """Muestra los datos anteriores formateados"""
        if obj.datos_anteriores:
            import json
            try:
                datos_formateados = json.dumps(obj.datos_anteriores, indent=2, ensure_ascii=False)
                return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 0.8rem;">{}</pre>', datos_formateados)
            except (TypeError, ValueError):
                return str(obj.datos_anteriores)
        return '-'
    datos_anteriores_display.short_description = '📋 Datos Anteriores'
    
    def datos_nuevos_display(self, obj):
        """Muestra los datos nuevos formateados"""
        if obj.datos_nuevos:
            import json
            try:
                datos_formateados = json.dumps(obj.datos_nuevos, indent=2, ensure_ascii=False)
                return format_html('<pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-size: 0.8rem;">{}</pre>', datos_formateados)
            except (TypeError, ValueError):
                return str(obj.datos_nuevos)
        return '-'
    datos_nuevos_display.short_description = '📋 Datos Nuevos'
    
    def get_queryset(self, request):
        """Optimiza las consultas con select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related('usuario', 'empresa')
    
    def changelist_view(self, request, extra_context=None):
        """Personaliza la vista de lista con información adicional"""
        extra_context = extra_context or {}
        
        # Estadísticas para el contexto
        total_registros = HistorialCambios.objects.count()
        registros_admins = HistorialCambios.objects.filter(usuario__is_superuser=True).count()
        registros_usuarios = total_registros - registros_admins
        
        extra_context.update({
            'total_registros': total_registros,
            'registros_admins': registros_admins,
            'registros_usuarios': registros_usuarios,
            'admin_holding_url': '/empresas/admin/historial/',
        })
        
        return super().changelist_view(request, extra_context=extra_context)
    
    class Media:
        css = {
            'all': ('admin/css/historial_cambios.css',)
        }
        js = ('admin/js/historial_cambios.js',)
