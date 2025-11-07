from django.contrib import admin
from core.admin_mixins import EmpresaFilterMixin
from core.admin_site import admin_site
from .models import Tercero, Impuesto, MetodoPago, Producto

@admin.register(Tercero, site=admin_site)
class TerceroAdmin(EmpresaFilterMixin, admin.ModelAdmin):
    list_display = ('razon_social', 'tipo_documento', 'numero_documento', 'email', 'empresa')
    list_filter = ('tipo_documento', 'tipo_tercero')
    search_fields = ('razon_social', 'numero_documento', 'email')
    autocomplete_fields = ['empresa']

@admin.register(Impuesto, site=admin_site)
class ImpuestoAdmin(EmpresaFilterMixin, admin.ModelAdmin):
    list_display = ('nombre', 'porcentaje', 'empresa')
    search_fields = ('nombre',)
    autocomplete_fields = ['empresa']

@admin.register(MetodoPago, site=admin_site)
class MetodoPagoAdmin(EmpresaFilterMixin, admin.ModelAdmin):
    list_display = ('nombre', 'empresa')
    search_fields = ('nombre',)
    autocomplete_fields = ['empresa']

@admin.register(Producto, site=admin_site)
class ProductoAdmin(EmpresaFilterMixin, admin.ModelAdmin):
    list_display = ('nombre', 'precio_venta', 'empresa')
    search_fields = ('nombre', 'descripcion')
    autocomplete_fields = ['empresa']
