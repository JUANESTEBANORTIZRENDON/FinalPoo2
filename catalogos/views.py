from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from empresas.middleware import EmpresaFilterMixin
from .models import Tercero, Impuesto, MetodoPago, Producto

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
        'telefono', 'email', 'regimen_tributario', 'observaciones', 'activo'
    ]
    success_url = reverse_lazy('catalogos:tercero_list')
    
    def form_valid(self, form):
        form.instance.empresa = self.get_empresa_activa()
        messages.success(self.request, f'Tercero {form.instance.razon_social} creado exitosamente.')
        return super().form_valid(form)

class TerceroUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = Tercero
    template_name = 'catalogos/tercero_form.html'
    fields = [
        'tipo_tercero', 'tipo_documento', 'numero_documento', 
        'razon_social', 'nombre_comercial', 'direccion', 'ciudad',
        'telefono', 'email', 'regimen_tributario', 'observaciones', 'activo'
    ]
    success_url = reverse_lazy('catalogos:tercero_list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Tercero {form.instance.razon_social} actualizado exitosamente.')
        return super().form_valid(form)

class TerceroDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = Tercero
    template_name = 'catalogos/tercero_confirm_delete.html'
    success_url = reverse_lazy('catalogos:tercero_list')

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

class MetodoPagoListView(LoginRequiredMixin, ListView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_lista.html'

class MetodoPagoDetailView(LoginRequiredMixin, DetailView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_detalle.html'

class MetodoPagoCreateView(LoginRequiredMixin, CreateView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_crear.html'
    fields = '__all__'

class MetodoPagoUpdateView(LoginRequiredMixin, UpdateView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_editar.html'
    fields = '__all__'

class MetodoPagoDeleteView(LoginRequiredMixin, DeleteView):
    model = MetodoPago
    template_name = 'catalogos/metodos_pago_eliminar.html'

class ProductoListView(LoginRequiredMixin, ListView):
    model = Producto
    template_name = 'catalogos/productos_lista.html'

class ProductoDetailView(LoginRequiredMixin, DetailView):
    model = Producto
    template_name = 'catalogos/productos_detalle.html'

class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    template_name = 'catalogos/productos_crear.html'
    fields = '__all__'

class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    template_name = 'catalogos/productos_editar.html'
    fields = '__all__'

class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'catalogos/productos_eliminar.html'

@login_required
def buscar_terceros(request):
    return JsonResponse({'results': []})

@login_required
def buscar_productos(request):
    return JsonResponse({'results': []})

@login_required
def info_producto(request, pk):
    return JsonResponse({'producto': {}})
