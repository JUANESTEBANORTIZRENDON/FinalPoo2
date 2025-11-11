from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from empresas.middleware import EmpresaFilterMixin
from .models import CuentaContable, Asiento, Partida

# Constante para evitar duplicación del literal 'contabilidad:asientos_detalle'
ASIENTOS_DETALLE_URL = 'contabilidad:asientos_detalle'
CUENTAS_LIST_URL = 'contabilidad:cuentas_lista'

# Vistas temporales básicas
class ContabilidadIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'contabilidad/index.html'

class CuentaContableListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_lista.html'
    context_object_name = 'object_list'
    paginate_by = 100
    
    def get_queryset(self):
        return super().get_queryset().order_by('codigo')

class CuentaContableDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_detalle.html'

class CuentaContableCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_crear.html'
    fields = ['codigo', 'nombre', 'descripcion', 'naturaleza', 'tipo_cuenta', 'cuenta_padre', 'nivel', 'acepta_movimiento', 'saldo_inicial', 'activa']
    success_url = reverse_lazy(CUENTAS_LIST_URL)
    
    def form_valid(self, form):
        form.instance.empresa = getattr(self.request, 'empresa_activa', None)
        messages.success(self.request, f'Cuenta contable {form.instance.codigo} - {form.instance.nombre} creada exitosamente.')
        return super().form_valid(form)

class CuentaContableUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_editar.html'
    fields = ['codigo', 'nombre', 'descripcion', 'naturaleza', 'tipo_cuenta', 'cuenta_padre', 'nivel', 'acepta_movimiento', 'saldo_inicial', 'activa']
    success_url = reverse_lazy(CUENTAS_LIST_URL)
    
    def form_valid(self, form):
        messages.success(self.request, f'Cuenta contable {form.instance.codigo} - {form.instance.nombre} actualizada exitosamente.')
        return super().form_valid(form)

class CuentaContableDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = CuentaContable
    template_name = 'contabilidad/cuentas_eliminar.html'
    success_url = reverse_lazy(CUENTAS_LIST_URL)
    
    def delete(self, request, *args, **kwargs):
        cuenta = self.get_object()
        messages.success(request, f'Cuenta contable {cuenta.codigo} - {cuenta.nombre} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

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
@require_http_methods(["POST"])
def crear_plan_cuentas_basico(request):
    return redirect('contabilidad:cuentas_lista')

@login_required
@require_http_methods(["POST"])
def confirmar_asiento(request, pk):
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def anular_asiento(request, pk):
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def duplicar_asiento(request, pk):
    return redirect('contabilidad:asientos_crear')

@login_required
@require_http_methods(["POST"])
def reversar_asiento(request, pk):
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["GET"])
def obtener_siguiente_numero_asiento(request):
    return JsonResponse({'numero': '000001'})

@login_required
@require_http_methods(["GET"])
def buscar_cuentas(request):
    return JsonResponse({'results': []})

@login_required
@require_http_methods(["POST"])
def validar_cuadre_asiento(request):
    return JsonResponse({'cuadrado': True})

@login_required
@require_http_methods(["GET"])
def obtener_saldo_cuenta(request, pk):
    return JsonResponse({'saldo': 0})
