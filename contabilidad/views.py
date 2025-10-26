from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CuentaContable, Asiento, Partida

# Constante para evitar duplicación del literal 'contabilidad:asientos_detalle'
ASIENTOS_DETALLE_URL = 'contabilidad:asientos_detalle'

# Vistas temporales básicas
class ContabilidadIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'contabilidad/index.html'

class CuentaContableListView(LoginRequiredMixin, ListView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_lista.html'

class CuentaContableDetailView(LoginRequiredMixin, DetailView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_detalle.html'

class CuentaContableCreateView(LoginRequiredMixin, CreateView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_crear.html'
    fields = '__all__'

class CuentaContableUpdateView(LoginRequiredMixin, UpdateView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_editar.html'
    fields = '__all__'

class CuentaContableDeleteView(LoginRequiredMixin, DeleteView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_eliminar.html'

class AsientoListView(LoginRequiredMixin, ListView):
    model = Asiento
    template_name = 'contabilidad/asientos_lista.html'

class AsientoDetailView(LoginRequiredMixin, DetailView):
    model = Asiento
    template_name = 'contabilidad/asientos_detalle.html'

class AsientoCreateView(LoginRequiredMixin, CreateView):
    model = Asiento
    template_name = 'contabilidad/asientos_crear.html'
    fields = '__all__'

class AsientoUpdateView(LoginRequiredMixin, UpdateView):
    model = Asiento
    template_name = 'contabilidad/asientos_editar.html'
    fields = '__all__'

class AsientoDeleteView(LoginRequiredMixin, DeleteView):
    model = Asiento
    template_name = 'contabilidad/asientos_eliminar.html'

class PartidaListView(LoginRequiredMixin, ListView):
    model = Partida
    template_name = 'contabilidad/partidas_lista.html'

class PartidaCreateView(LoginRequiredMixin, CreateView):
    model = Partida
    template_name = 'contabilidad/partidas_crear.html'
    fields = '__all__'

class PartidaUpdateView(LoginRequiredMixin, UpdateView):
    model = Partida
    template_name = 'contabilidad/partidas_editar.html'
    fields = '__all__'

class PartidaDeleteView(LoginRequiredMixin, DeleteView):
    model = Partida
    template_name = 'contabilidad/partidas_eliminar.html'

class ConsultaSaldosView(LoginRequiredMixin, TemplateView):
    template_name = 'contabilidad/consulta_saldos.html'

class ConsultaMovimientosView(LoginRequiredMixin, TemplateView):
    template_name = 'contabilidad/consulta_movimientos.html'

class ConsultaCuentaView(LoginRequiredMixin, TemplateView):
    template_name = 'contabilidad/consulta_cuenta.html'

@login_required
def crear_plan_cuentas_basico(request):
    return redirect('contabilidad:cuentas_lista')

@login_required
def confirmar_asiento(request, pk):
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
def anular_asiento(request, pk):
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
def duplicar_asiento(request, pk):
    return redirect('contabilidad:asientos_crear')

@login_required
def reversar_asiento(request, pk):
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
def obtener_siguiente_numero_asiento(request):
    return JsonResponse({'numero': '000001'})

@login_required
def buscar_cuentas(request):
    return JsonResponse({'results': []})

@login_required
def validar_cuadre_asiento(request):
    return JsonResponse({'cuadrado': True})

@login_required
def obtener_saldo_cuenta(request, pk):
    return JsonResponse({'saldo': 0})
