from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        productos = context['productos']
        
        # Calcular estadísticas
        total_stock = sum(p.stock_actual for p in productos if p.inventariable)
        productos_fisicos = sum(1 for p in productos if p.tipo_producto == 'producto')
        productos_bajo_stock = sum(1 for p in productos if p.requiere_reposicion)
        
        context['total_stock'] = total_stock
        context['productos_fisicos'] = productos_fisicos
        context['productos_bajo_stock'] = productos_bajo_stock
        
        return context

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
        messages.success(self.request, f'Producto "{form.instance.nombre}" actualizado exitosamente.')
        return super().form_valid(form)

@login_required
@require_POST
def producto_toggle_activo(request, pk):
    """
    Activa o desactiva un producto.
    Los productos inactivos no se pueden comprar/vender.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    producto = get_object_or_404(Producto, pk=pk, empresa=empresa_activa)
    
    # Cambiar el estado
    producto.activo = not producto.activo
    producto.save()
    
    estado = "activado" if producto.activo else "desactivado"
    messages.success(request, f'Producto "{producto.nombre}" {estado} exitosamente.')
    
    return redirect('catalogos:producto_list')

@login_required
@require_http_methods(["GET"])
def buscar_terceros(request):
    return JsonResponse({'results': []})

@login_required
@require_http_methods(["GET"])
def buscar_productos(request):
    """
    Busca productos activos para ventas/compras.
    Solo devuelve productos activos que pueden ser vendidos.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    if not empresa_activa:
        return JsonResponse({'results': []})
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    # Buscar solo productos activos
    productos = Producto.objects.filter(
        empresa=empresa_activa,
        activo=True  # Solo productos activos
    ).filter(
        models.Q(nombre__icontains=query) |
        models.Q(codigo__icontains=query)
    ).select_related('impuesto')[:20]
    
    results = []
    for producto in productos:
        results.append({
            'id': producto.id,
            'codigo': producto.codigo,
            'nombre': producto.nombre,
            'precio_venta': str(producto.precio_venta),
            'precio_con_impuesto': str(producto.precio_con_impuesto),
            'impuesto': {
                'id': producto.impuesto.id if producto.impuesto else None,
                'nombre': producto.impuesto.nombre if producto.impuesto else None,
                'porcentaje': str(producto.impuesto.porcentaje) if producto.impuesto else '0'
            },
            'inventariable': producto.inventariable,
            'stock_actual': str(producto.stock_actual)
        })
    
    return JsonResponse({'results': results})

@login_required
@require_http_methods(["GET"])
def info_producto(request, pk):
    """
    Obtiene información detallada de un producto activo.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    if not empresa_activa:
        return JsonResponse({'error': 'No hay empresa activa'}, status=400)
    
    try:
        # Solo devolver información si el producto está activo
        producto = Producto.objects.select_related('impuesto').get(
            pk=pk,
            empresa=empresa_activa,
            activo=True  # Solo productos activos
        )
        
        return JsonResponse({
            'producto': {
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'tipo_producto': producto.tipo_producto,
                'precio_venta': str(producto.precio_venta),
                'precio_costo': str(producto.precio_costo),
                'precio_con_impuesto': str(producto.precio_con_impuesto),
                'impuesto': {
                    'id': producto.impuesto.id if producto.impuesto else None,
                    'nombre': producto.impuesto.nombre if producto.impuesto else None,
                    'porcentaje': str(producto.impuesto.porcentaje) if producto.impuesto else '0'
                },
                'inventariable': producto.inventariable,
                'stock_actual': str(producto.stock_actual),
                'stock_minimo': str(producto.stock_minimo),
                'requiere_reposicion': producto.requiere_reposicion
            }
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado o inactivo'}, status=404)
