from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Factura, FacturaDetalle

# Vistas temporales básicas
class FacturaListView(LoginRequiredMixin, ListView):
    model = Factura
    template_name = 'facturacion/lista.html'

class FacturaDetailView(LoginRequiredMixin, DetailView):
    model = Factura
    template_name = 'facturacion/detalle.html'

class FacturaCreateView(LoginRequiredMixin, CreateView):
    """
    View para crear una nueva factura.
    """
    model = Factura
    template_name = 'facturacion/crear.html'
    fields = [
        'cliente', 'fecha_factura', 'fecha_vencimiento', 'tipo_venta',
        'metodo_pago', 'observaciones'
    ]
    success_url = reverse_lazy('facturacion:lista')

    def form_valid(self, form):
        """
        Set the empresa field and show success message.
        """
        # Set the empresa field to the user's active company
        # Assuming you have a method to get the active company
        # form.instance.empresa = self.request.user.empresa_activa
        
        # Set the numero_factura (you might want to generate this automatically)
        # form.instance.numero_factura = self.generar_numero_factura()
        
        messages.success(
            self.request,
            'La factura se ha creado correctamente.'
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add additional context to the template."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear Nueva Factura'
        return context

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
def confirmar_factura(request, pk):
    return redirect('facturacion:detalle', pk=pk)

@login_required
def anular_factura(request, pk):
    return redirect('facturacion:detalle', pk=pk)

@login_required
def duplicar_factura(request, pk):
    return redirect('facturacion:crear')

@login_required
def factura_pdf(request, pk):
    return HttpResponse("PDF")

@login_required
def factura_imprimir(request, pk):
    return HttpResponse("Imprimir")

@login_required
def exportar_facturas(request):
    return HttpResponse("Exportar")

@login_required
def obtener_siguiente_numero(request):
    return JsonResponse({'numero': '000001'})

@login_required
def calcular_totales_factura(request):
    return JsonResponse({'totales': {}})
