from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Factura, FacturaDetalle

# Constante para evitar duplicación del literal de URL
FACTURA_DETALLE_URL = 'facturacion:detalle'

# Vistas temporales básicas
class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'facturacion/lista.html'
    context_object_name = 'object_list'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        if empresa_activa:
            queryset = queryset.filter(empresa=empresa_activa)
        
        # Filtros de búsqueda
        cliente = self.request.GET.get('cliente')
        numero_factura = self.request.GET.get('numero_factura')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        
        if cliente:
            queryset = queryset.filter(
                Q(cliente__razon_social__icontains=cliente) |
                Q(cliente__numero_documento__icontains=cliente)
            )
        
        if numero_factura:
            queryset = queryset.filter(numero_factura__icontains=numero_factura)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_factura__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_factura__lte=fecha_hasta)
        
        return queryset.order_by('-fecha_factura', '-numero_factura')

class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'facturacion/detalle.html'

class FacturaCreateView(LoginRequiredMixin, CreateView):
    model = Factura
    template_name = 'facturacion/crear.html'
    fields = '__all__'

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
