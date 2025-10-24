from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Pago, CuentaBancaria

# Vistas temporales básicas
class TesoreriaIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/index.html'

class PagoListView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'tesoreria/pagos_lista.html'

class PagoDetailView(LoginRequiredMixin, DetailView):
    model = Pago
    template_name = 'tesoreria/pagos_detalle.html'

class PagoCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    template_name = 'tesoreria/pagos_crear.html'
    fields = '__all__'

class PagoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pago
    template_name = 'tesoreria/pagos_editar.html'
    fields = '__all__'

class PagoDeleteView(LoginRequiredMixin, DeleteView):
    model = Pago
    template_name = 'tesoreria/pagos_eliminar.html'

class CobroListView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'tesoreria/cobros_lista.html'

class CobroCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    template_name = 'tesoreria/cobros_crear.html'
    fields = '__all__'

class EgresoListView(LoginRequiredMixin, ListView):
    model = Pago
    template_name = 'tesoreria/egresos_lista.html'

class EgresoCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    template_name = 'tesoreria/egresos_crear.html'
    fields = '__all__'

class CuentaBancariaListView(LoginRequiredMixin, ListView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_lista.html'

class CuentaBancariaDetailView(LoginRequiredMixin, DetailView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_detalle.html'

class CuentaBancariaCreateView(LoginRequiredMixin, CreateView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_crear.html'
    fields = '__all__'

class CuentaBancariaUpdateView(LoginRequiredMixin, UpdateView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_editar.html'
    fields = '__all__'

class CuentaBancariaDeleteView(LoginRequiredMixin, DeleteView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_eliminar.html'

class FlujoCajaView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/flujo_caja.html'

class SaldosCuentasView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/saldos_cuentas.html'

class PagosPeriodoView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/pagos_periodo.html'

@login_required
def confirmar_pago(request, pk):
    return redirect('tesoreria:pagos_detalle', pk=pk)

@login_required
def anular_pago(request, pk):
    return redirect('tesoreria:pagos_detalle', pk=pk)

@login_required
def cobrar_factura(request, factura_pk):
    return redirect('tesoreria:cobros_crear')

@login_required
def obtener_siguiente_numero_pago(request):
    return JsonResponse({'numero': '000001'})

@login_required
def facturas_pendientes_tercero(request, tercero_pk):
    return JsonResponse({'facturas': []})
