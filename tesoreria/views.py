from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from .models import Pago, CuentaBancaria
from .forms import CobroForm
from empresas.middleware import EmpresaFilterMixin

# Constante para evitar duplicación del literal de URL
PAGOS_DETALLE_URL = 'tesoreria:pagos_detalle'

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

class CobroListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Pago
    template_name = 'tesoreria/cobros_lista.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(tipo_pago='cobro')
        
        # Filtros opcionales
        cliente = self.request.GET.get('cliente')
        fecha_desde = self.request.GET.get('fecha_desde')
        fecha_hasta = self.request.GET.get('fecha_hasta')
        estado = self.request.GET.get('estado')
        
        if cliente:
            queryset = queryset.filter(tercero__razon_social__icontains=cliente)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_pago__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_pago__lte=fecha_hasta)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.select_related('tercero', 'metodo_pago').order_by('-fecha_pago', '-numero_pago')

class CobroCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Pago
    form_class = CobroForm
    template_name = 'tesoreria/cobros_crear.html'
    success_url = reverse_lazy('tesoreria:cobros_lista')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = getattr(self.request, 'empresa_activa', None)
        return kwargs
    
    def form_valid(self, form):
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        if not empresa_activa:
            messages.error(self.request, 'Debes seleccionar una empresa.')
            return redirect('empresas:cambiar_empresa')
        
        # Generar número de cobro automático
        ultimo_cobro = Pago.objects.filter(
            empresa=empresa_activa,
            tipo_pago='cobro'
        ).order_by('-numero_pago').first()
        
        if ultimo_cobro:
            try:
                ultimo_numero = int(ultimo_cobro.numero_pago.replace('COB-', ''))
                nuevo_numero = f'COB-{(ultimo_numero + 1):06d}'
            except (ValueError, AttributeError):
                nuevo_numero = 'COB-000001'
        else:
            nuevo_numero = 'COB-000001'
        
        # Configurar el cobro
        form.instance.empresa = empresa_activa
        form.instance.tipo_pago = 'cobro'
        form.instance.numero_pago = nuevo_numero
        form.instance.creado_por = self.request.user
        form.instance.estado = 'borrador'
        
        messages.success(
            self.request,
            f'Cobro {nuevo_numero} registrado exitosamente por ${form.instance.valor:,.2f}'
        )
        
        return super().form_valid(form)

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
@require_http_methods(["POST"])
def confirmar_pago(request, pk):
    return redirect(PAGOS_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def anular_pago(request, pk):
    return redirect(PAGOS_DETALLE_URL, pk=pk)

@login_required
@require_safe
def cobrar_factura(request, factura_pk):
    return redirect('tesoreria:cobros_crear')

@login_required
@require_http_methods(["GET"])
def obtener_siguiente_numero_pago(request):
    return JsonResponse({'numero': '000001'})

@login_required
@require_http_methods(["GET"])
def facturas_pendientes_tercero(request, tercero_pk):
    return JsonResponse({'facturas': []})
