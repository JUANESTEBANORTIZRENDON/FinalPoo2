from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.db import models
from empresas.middleware import EmpresaFilterMixin
from .models import Tercero, Impuesto, MetodoPago, Producto

# Constantes para evitar duplicación de literales de URL
TERCERO_LIST_URL = 'catalogos:tercero_list'
PRODUCTO_LIST_URL = 'catalogos:producto_list'

# Vistas temporales básicas
class CatalogosIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'catalogos/index.html'

class TerceroListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Tercero
    template_name = 'catalogos/tercero_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        return super().get_queryset().order_by('razon_social')

class TerceroDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    model = Tercero
    template_name = 'catalogos/tercero_detail.html'

class TerceroCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Tercero
    template_name = 'catalogos/tercero_form.html'
    fields = [
        'tipo_tercero', 'tipo_documento', 'numero_documento', 
        'razon_social', 'nombre_comercial', 'direccion', 'ciudad',
        'departamento', 'telefono', 'email', 'activo'
    ]
    success_url = reverse_lazy(TERCERO_LIST_URL)
    
    def form_valid(self, form):
        form.instance.empresa = getattr(self.request, 'empresa_activa', None)
        messages.success(self.request, f'Tercero {form.instance.razon_social} creado exitosamente.')
        return super().form_valid(form)

class TerceroUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = Tercero
    template_name = 'catalogos/tercero_form.html'
    fields = [
        'tipo_tercero', 'tipo_documento', 'numero_documento', 
        'razon_social', 'nombre_comercial', 'direccion', 'ciudad',
        'departamento', 'telefono', 'email', 'activo'
    ]
    success_url = reverse_lazy(TERCERO_LIST_URL)
    
    def form_valid(self, form):
        messages.success(self.request, f'Tercero {form.instance.razon_social} actualizado exitosamente.')
        return super().form_valid(form)

class TerceroDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = Tercero
    template_name = 'catalogos/tercero_confirm_delete.html'
    success_url = reverse_lazy(TERCERO_LIST_URL)

class ImpuestoListView(LoginRequiredMixin, ListView):
    model = Impuesto
    template_name = 'catalogos/impuestos_lista.html'

class ImpuestoDetailView(LoginRequiredMixin, DetailView):
    model = Impuesto
    template_name = 'catalogos/impuestos_detalle.html'

class ImpuestoCreateView(LoginRequiredMixin, CreateView):
    model = Impuesto
    template_name = 'catalogos/impuestos_crear.html'
    fields = '__all__'

class ImpuestoUpdateView(LoginRequiredMixin, UpdateView):
    model = Impuesto
    template_name = 'catalogos/impuestos_editar.html'
    fields = '__all__'

class ImpuestoDeleteView(LoginRequiredMixin, DeleteView):
    model = Impuesto
    template_name = 'catalogos/impuestos_eliminar.html'

class MetodoPagoListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_lista.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.order_by('nombre')

class MetodoPagoDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_detalle.html'

class MetodoPagoCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_crear.html'
    fields = ['codigo', 'nombre', 'tipo_metodo', 'requiere_referencia', 'activo']
    success_url = reverse_lazy('catalogos:metodos_pago_lista')
    
    def form_valid(self, form):
        form.instance.empresa = self.request.empresa_activa
        return super().form_valid(form)

class MetodoPagoUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_editar.html'
    fields = ['codigo', 'nombre', 'tipo_metodo', 'requiere_referencia', 'activo']
    success_url = reverse_lazy('catalogos:metodos_pago_lista')

class MetodoPagoDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_eliminar.html'
    success_url = reverse_lazy('catalogos:metodos_pago_lista')

class ProductoListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Producto
    template_name = 'catalogos/productos_lista.html'
    context_object_name = 'productos'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionales
        buscar = self.request.GET.get('buscar')
        tipo = self.request.GET.get('tipo')
        
        if buscar:
            queryset = queryset.filter(
                models.Q(nombre__icontains=buscar) |
                models.Q(codigo__icontains=buscar)
            )
        
        if tipo:
            queryset = queryset.filter(tipo_producto=tipo)
        
        return queryset.select_related('impuesto').order_by('nombre')

class ProductoDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    model = Producto
    template_name = 'catalogos/productos_detalle.html'

class ProductoCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Producto
    template_name = 'catalogos/productos_crear.html'
    fields = [
        'codigo', 'nombre', 'descripcion', 'tipo_producto',
        'precio_venta', 'precio_costo', 'impuesto',
        'inventariable', 'stock_actual', 'stock_minimo', 'activo'
    ]
    success_url = reverse_lazy(PRODUCTO_LIST_URL)
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        # Filtrar impuestos por empresa
        if empresa_activa and 'impuesto' in form.fields:
            from catalogos.models import Impuesto
            form.fields['impuesto'].queryset = Impuesto.objects.filter(
                empresa=empresa_activa,
                activo=True
            )
        
        # Agregar clases CSS
        for field_name, field in form.fields.items():
            if field_name == 'descripcion':
                field.widget.attrs.update({'class': 'form-control', 'rows': 3})
            elif field_name in ['inventariable', 'activo']:
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name == 'tipo_producto':
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'impuesto':
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        return form
    
    def form_valid(self, form):
        form.instance.empresa = getattr(self.request, 'empresa_activa', None)
        messages.success(self.request, f'Producto "{form.instance.nombre}" creado exitosamente.')
        return super().form_valid(form)

class ProductoUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = Producto
    template_name = 'catalogos/productos_editar.html'
    fields = [
        'codigo', 'nombre', 'descripcion', 'tipo_producto',
        'precio_venta', 'precio_costo', 'impuesto',
        'inventariable', 'stock_actual', 'stock_minimo', 'activo'
    ]
    success_url = reverse_lazy(PRODUCTO_LIST_URL)
    
    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)

class ProductoDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = Producto
    template_name = 'catalogos/productos_eliminar.html'
    success_url = reverse_lazy(PRODUCTO_LIST_URL)

@login_required
@require_http_methods(["GET"])
def buscar_terceros(request):
    return JsonResponse({'results': []})

@login_required
@require_http_methods(["GET"])
def buscar_productos(request):
    return JsonResponse({'results': []})

@login_required
@require_http_methods(["GET"])
def info_producto(request, pk):
    return JsonResponse({'producto': {}})
