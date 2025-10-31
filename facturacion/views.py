from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from .models import Factura, FacturaDetalle

# Vistas temporales básicas
class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'facturacion/lista.html'

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
    return redirect('facturacion:detalle', pk=pk)

@login_required
@require_http_methods(["POST"])
def anular_factura(request, pk):
    return redirect('facturacion:detalle', pk=pk)

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
