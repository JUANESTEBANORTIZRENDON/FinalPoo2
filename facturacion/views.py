from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import Factura, FacturaDetalle
from catalogos.models import Tercero, Producto, MetodoPago

# Constante para evitar duplicación del literal de URL
FACTURA_DETALLE_URL = 'facturacion:detalle'

# Constante para evitar duplicación del literal de URL
FACTURA_DETALLE_URL = 'facturacion:detalle'

# Vistas temporales básicas
class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'facturacion/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por empresa activa
        if hasattr(self.request, 'empresa_activa'):
            queryset = queryset.filter(empresa=self.request.empresa_activa)
        return queryset.select_related('cliente', 'empresa', 'creado_por')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar estadísticas
        facturas = self.get_queryset()
        context['total_facturas'] = facturas.count()
        context['facturas_borrador'] = facturas.filter(estado='borrador').count()
        context['facturas_confirmadas'] = facturas.filter(estado='confirmada').count()
        context['facturas_anuladas'] = facturas.filter(estado='anulada').count()
        return context

class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'facturacion/detalle.html'

class FacturaCreateView(LoginRequiredMixin, CreateView):
    model = Factura
    template_name = 'facturacion/factura_create.html'
    fields = ['cliente', 'fecha_factura', 'tipo_venta', 'metodo_pago', 'fecha_vencimiento', 'observaciones']
    success_url = reverse_lazy('facturacion:factura_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener clientes para el select
        if hasattr(self.request, 'empresa_activa'):
            context['clientes'] = Tercero.objects.filter(
                empresa=self.request.empresa_activa,
                tipo_tercero__in=['cliente', 'ambos']
            ).order_by('razon_social')
            context['metodos_pago'] = MetodoPago.objects.filter(
                empresa=self.request.empresa_activa
            ).order_by('nombre')
            context['productos'] = Producto.objects.filter(
                empresa=self.request.empresa_activa,
                activo=True
            ).select_related('impuesto').order_by('nombre')
        # Agregar fecha actual
        context['today'] = timezone.now().date()
        return context
    
    def form_valid(self, form):
        # Asignar empresa activa
        if hasattr(self.request, 'empresa_activa'):
            form.instance.empresa = self.request.empresa_activa
        
        # Asignar usuario creador
        form.instance.creado_por = self.request.user
        
        # Generar número de factura automáticamente
        form.instance.numero_factura = self.generar_numero_factura()
        
        # Estado inicial: borrador (pendiente)
        form.instance.estado = 'borrador'
        
        # Inicializar totales en cero
        form.instance.subtotal = Decimal('0.00')
        form.instance.total_impuestos = Decimal('0.00')
        form.instance.total = Decimal('0.00')
        
        messages.success(self.request, f'Factura {form.instance.numero_factura} creada exitosamente en estado pendiente.')
        return super().form_valid(form)
    
    def generar_numero_factura(self):
        """Genera el siguiente número de factura para la empresa"""
        empresa = self.request.empresa_activa if hasattr(self.request, 'empresa_activa') else None
        if empresa:
            ultima_factura = Factura.objects.filter(empresa=empresa).order_by('-numero_factura').first()
            if ultima_factura:
                try:
                    numero = int(ultima_factura.numero_factura) + 1
                    return str(numero).zfill(6)
                except ValueError:
                    pass
        return '000001'

class FacturaUpdateView(LoginRequiredMixin, UpdateView):
    model = Factura
    template_name = 'facturacion/editar.html'
    fields = '__all__'

class FacturaDeleteView(LoginRequiredMixin, DeleteView):
    model = Factura
    template_name = 'facturacion/eliminar.html'

class FacturaDetalleListView(LoginRequiredMixin, ListView):
    model = FacturaDetalle
    template_name = 'facturacion/detalles_lista.html'

class FacturaDetalleCreateView(LoginRequiredMixin, CreateView):
    model = FacturaDetalle
    template_name = 'facturacion/detalles_crear.html'
    fields = '__all__'

class FacturaDetalleUpdateView(LoginRequiredMixin, UpdateView):
    model = FacturaDetalle
    template_name = 'facturacion/detalles_editar.html'
    fields = '__all__'

class FacturaDetalleDeleteView(LoginRequiredMixin, DeleteView):
    model = FacturaDetalle
    template_name = 'facturacion/detalles_eliminar.html'

class FacturaReporteView(LoginRequiredMixin, TemplateView):
    template_name = 'facturacion/reporte.html'

@login_required
@require_http_methods(["POST"])
def confirmar_factura(request, pk):
    return redirect(FACTURA_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def anular_factura(request, pk):
    return redirect(FACTURA_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def duplicar_factura(request, pk):
    return redirect('facturacion:crear')

@login_required
@require_http_methods(["GET"])
def factura_pdf(request, pk):
    return HttpResponse("PDF")

@login_required
@require_http_methods(["GET"])
def factura_imprimir(request, pk):
    return HttpResponse("Imprimir")

@login_required
@require_http_methods(["GET"])
def exportar_facturas(request):
    return HttpResponse("Exportar")

@login_required
@require_http_methods(["GET"])
def obtener_siguiente_numero(request):
    return JsonResponse({'numero': '000001'})

@login_required
@require_http_methods(["POST"])
def calcular_totales_factura(request):
    return JsonResponse({'totales': {}})
