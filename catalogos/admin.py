from django.contrib import admin
from .models import Tercero, Impuesto, MetodoPago, Producto

@admin.register(Tercero)
class TerceroAdmin(admin.ModelAdmin):
    list_display = ('razon_social', 'tipo_documento', 'numero_documento', 'email', 'empresa')
    list_filter = ('tipo_documento', 'tipo_tercero', 'empresa')
    search_fields = ('razon_social', 'numero_documento', 'email')

@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('nombre',)

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_venta', 'empresa')
    list_filter = ('empresa',)
    search_fields = ('nombre', 'descripcion')
