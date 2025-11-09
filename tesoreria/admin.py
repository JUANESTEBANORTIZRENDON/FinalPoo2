from django.contrib import admin
from .models import Pago, PagoDetalle, CuentaBancaria

class PagoDetalleInline(admin.TabularInline):
    model = PagoDetalle
    extra = 1
    fields = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['subtotal']

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['numero_pago', 'tipo_pago', 'tercero', 'valor', 'fecha_pago', 'estado']
    list_filter = ['tipo_pago', 'estado', 'fecha_pago']
    search_fields = ['numero_pago', 'tercero__razon_social']
    inlines = [PagoDetalleInline]

@admin.register(CuentaBancaria)
class CuentaBancariaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'tipo_cuenta', 'saldo_actual']
    list_filter = ['tipo_cuenta']
    search_fields = ['codigo', 'nombre']
