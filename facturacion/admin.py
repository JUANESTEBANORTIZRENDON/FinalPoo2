from django.contrib import admin
from .models import Factura, FacturaDetalle

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('numero_factura', 'cliente', 'fecha_factura', 'total', 'estado', 'empresa')
    list_filter = ('estado', 'fecha_factura', 'empresa')
    search_fields = ('numero_factura', 'cliente__razon_social')
    readonly_fields = ('fecha_creacion',)

@admin.register(FacturaDetalle)
class FacturaDetalleAdmin(admin.ModelAdmin):
    list_display = ('factura', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
    list_filter = ('factura__empresa',)
    search_fields = ('factura__numero_factura', 'producto__nombre')
