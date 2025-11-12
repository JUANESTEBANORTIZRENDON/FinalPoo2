from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import models
from empresas.middleware import EmpresaFilterMixin
from .models import CuentaContable, Asiento, Partida

# Constantes para evitar duplicación de literales de URL
ASIENTOS_DETALLE_URL = 'contabilidad:asientos_detalle'
ASIENTOS_LIST_URL = 'contabilidad:asientos_lista'
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

class AsientoListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Asiento
    template_name = 'contabilidad/asientos_lista.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        return super().get_queryset().select_related('empresa', 'creado_por').order_by('-fecha_asiento', '-numero_asiento')

class AsientoDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    model = Asiento
    template_name = 'contabilidad/asientos_detalle.html'
    
    def get_queryset(self):
        return super().get_queryset().select_related('empresa', 'creado_por', 'confirmado_por').prefetch_related('partidas__cuenta')

class AsientoCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Asiento
    template_name = 'contabilidad/asientos_crear.html'
    fields = ['numero_asiento', 'fecha_asiento', 'tipo_asiento', 'concepto', 'observaciones']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        # Obtener cuentas contables activas que aceptan movimiento
        cuentas = CuentaContable.objects.filter(
            activa=True,
            acepta_movimiento=True
        )
        if empresa_activa:
            cuentas = cuentas.filter(empresa=empresa_activa)
        
        context['cuentas'] = cuentas.order_by('codigo')
        return context
    
    def form_valid(self, form):
        from decimal import Decimal
        import json
        
        # Guardar el asiento
        form.instance.empresa = getattr(self.request, 'empresa_activa', None)
        form.instance.creado_por = self.request.user
        form.instance.estado = 'borrador'
        
        # Obtener las partidas del POST (enviadas como JSON)
        partidas_json = self.request.POST.get('partidas_data', '[]')
        
        try:
            partidas_data = json.loads(partidas_json)
        except json.JSONDecodeError:
            messages.error(self.request, 'Error al procesar las partidas. Datos inv\u00e1lidos.')
            return self.form_invalid(form)
        
        # Validar que hay partidas
        if not partidas_data or len(partidas_data) == 0:
            messages.error(self.request, 'Debe agregar al menos una partida al asiento.')
            return self.form_invalid(form)
        
        # Calcular totales
        total_debito = Decimal('0.00')
        total_credito = Decimal('0.00')
        
        for partida in partidas_data:
            total_debito += Decimal(str(partida.get('debito', 0)))
            total_credito += Decimal(str(partida.get('credito', 0)))
        
        # Validar cuadre
        if abs(total_debito - total_credito) > Decimal('0.01'):
            messages.error(self.request, f'El asiento no est\u00e1 cuadrado. D\u00e9bitos: ${total_debito}, Cr\u00e9ditos: ${total_credito}')
            return self.form_invalid(form)
        
        # Asignar totales
        form.instance.total_debito = total_debito
        form.instance.total_credito = total_credito
        
        # Guardar el asiento
        asiento = form.save()
        
        # Crear las partidas
        orden = 1
        for partida_data in partidas_data:
            try:
                cuenta_id = partida_data.get('cuenta_id')
                if not cuenta_id:
                    continue
                
                cuenta = CuentaContable.objects.get(pk=cuenta_id, empresa=form.instance.empresa)
                
                Partida.objects.create(
                    asiento=asiento,
                    cuenta=cuenta,
                    concepto=partida_data.get('concepto', ''),
                    valor_debito=Decimal(str(partida_data.get('debito', 0))),
                    valor_credito=Decimal(str(partida_data.get('credito', 0))),
                    orden=orden
                )
                orden += 1
            except CuentaContable.DoesNotExist:
                messages.warning(self.request, f'Cuenta con ID {cuenta_id} no encontrada. Partida omitida.')
                continue
            except Exception as e:
                messages.warning(self.request, f'Error al crear partida: {str(e)}')
                continue
        
        messages.success(self.request, f'Asiento {asiento.numero_asiento} creado exitosamente con {orden-1} partidas.')
        return redirect(ASIENTOS_DETALLE_URL, pk=asiento.pk)

class AsientoUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = Asiento
    template_name = 'contabilidad/asientos_editar.html'
    fields = ['numero_asiento', 'fecha_asiento', 'tipo_asiento', 'concepto', 'observaciones']
    success_url = reverse_lazy(ASIENTOS_LIST_URL)
    
    def form_valid(self, form):
        if not form.instance.puede_editarse:
            messages.error(self.request, 'No se puede editar un asiento confirmado o anulado.')
            return redirect(ASIENTOS_DETALLE_URL, pk=form.instance.pk)
        messages.success(self.request, f'Asiento {form.instance.numero_asiento} actualizado exitosamente.')
        return super().form_valid(form)

class AsientoDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = Asiento
    template_name = 'contabilidad/asientos_eliminar.html'
    success_url = reverse_lazy(ASIENTOS_LIST_URL)
    
    def delete(self, request, *args, **kwargs):
        asiento = self.get_object()
        if not asiento.puede_editarse:
            messages.error(request, 'No se puede eliminar un asiento confirmado o anulado.')
            return redirect(ASIENTOS_DETALLE_URL, pk=asiento.pk)
        messages.success(request, f'Asiento {asiento.numero_asiento} eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class PartidaListView(LoginRequiredMixin, ListView):
    model = Partida
    template_name = 'contabilidad/partidas_lista.html'
    context_object_name = 'object_list'
    paginate_by = 100
    
    def get_queryset(self):
        queryset = super().get_queryset()
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        if empresa_activa:
            queryset = queryset.filter(asiento__empresa=empresa_activa)
        return queryset.select_related('asiento__empresa', 'cuenta').order_by('-asiento__fecha_asiento')

class PartidaCreateView(LoginRequiredMixin, CreateView):
    model = Partida
    template_name = 'contabilidad/partidas_crear.html'
    fields = ['asiento', 'cuenta', 'concepto', 'valor_debito', 'valor_credito', 'orden', 'tercero']
    
    def form_valid(self, form):
        # Validar que el asiento pertenece a la empresa activa
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        if empresa_activa and form.instance.asiento.empresa != empresa_activa:
            messages.error(self.request, 'El asiento no pertenece a la empresa activa.')
            return self.form_invalid(form)
        messages.success(self.request, 'Partida creada exitosamente.')
        return super().form_valid(form)

class PartidaUpdateView(LoginRequiredMixin, UpdateView):
    model = Partida
    template_name = 'contabilidad/partidas_editar.html'
    fields = ['asiento', 'cuenta', 'concepto', 'valor_debito', 'valor_credito', 'orden', 'tercero']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        if empresa_activa:
            queryset = queryset.filter(asiento__empresa=empresa_activa)
        return queryset
    
    def form_valid(self, form):
        # Validar que el asiento pertenece a la empresa activa
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        if empresa_activa and form.instance.asiento.empresa != empresa_activa:
            messages.error(self.request, 'El asiento no pertenece a la empresa activa.')
            return self.form_invalid(form)
        messages.success(self.request, 'Partida actualizada exitosamente.')
        return super().form_valid(form)

class PartidaDeleteView(LoginRequiredMixin, DeleteView):
    model = Partida
    template_name = 'contabilidad/partidas_eliminar.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        if empresa_activa:
            queryset = queryset.filter(asiento__empresa=empresa_activa)
        return queryset
    
    def get_success_url(self):
        return reverse_lazy(ASIENTOS_DETALLE_URL, kwargs={'pk': self.object.asiento.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Partida eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

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
    """
    Confirma un asiento contable en estado borrador.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    asiento = get_object_or_404(Asiento, pk=pk)
    
    # Verificar permisos
    if empresa_activa and asiento.empresa != empresa_activa:
        messages.error(request, 'No tienes permiso para confirmar este asiento.')
        return redirect(ASIENTOS_LIST_URL)
    
    # Verificar que esté en borrador
    if asiento.estado != 'borrador':
        messages.error(request, 'Solo se pueden confirmar asientos en estado borrador.')
        return redirect(ASIENTOS_DETALLE_URL, pk=pk)
    
    # Verificar que esté cuadrado
    if not asiento.esta_cuadrado:
        messages.error(request, 'El asiento no está cuadrado. Los débitos deben ser iguales a los créditos.')
        return redirect(ASIENTOS_DETALLE_URL, pk=pk)
    
    # Confirmar el asiento
    asiento.estado = 'confirmado'
    asiento.confirmado_por = request.user
    asiento.fecha_confirmacion = timezone.now()
    asiento.save()
    
    # Actualizar saldos de las cuentas
    for partida in asiento.partidas.all():
        cuenta = partida.cuenta
        cuenta.saldo_debito += partida.valor_debito
        cuenta.saldo_credito += partida.valor_credito
        cuenta.save()
    
    messages.success(request, f'Asiento {asiento.numero_asiento} confirmado exitosamente.')
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def anular_asiento(request, pk):
    """
    Anula un asiento contable confirmado.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    asiento = get_object_or_404(Asiento, pk=pk)
    
    # Verificar permisos
    if empresa_activa and asiento.empresa != empresa_activa:
        messages.error(request, 'No tienes permiso para anular este asiento.')
        return redirect(ASIENTOS_LIST_URL)
    
    # Verificar que esté confirmado
    if asiento.estado != 'confirmado':
        messages.error(request, 'Solo se pueden anular asientos confirmados.')
        return redirect(ASIENTOS_DETALLE_URL, pk=pk)
    
    # Reversar saldos de las cuentas
    for partida in asiento.partidas.all():
        cuenta = partida.cuenta
        cuenta.saldo_debito -= partida.valor_debito
        cuenta.saldo_credito -= partida.valor_credito
        cuenta.save()
    
    # Anular el asiento
    asiento.estado = 'anulado'
    asiento.save()
    
    messages.success(request, f'Asiento {asiento.numero_asiento} anulado exitosamente.')
    return redirect(ASIENTOS_DETALLE_URL, pk=pk)

@login_required
@require_http_methods(["POST"])
def duplicar_asiento(request, pk):
    """
    Duplica un asiento contable creando uno nuevo con los mismos datos.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    asiento_original = get_object_or_404(Asiento, pk=pk)
    
    # Verificar permisos
    if empresa_activa and asiento_original.empresa != empresa_activa:
        messages.error(request, 'No tienes permiso para duplicar este asiento.')
        return redirect(ASIENTOS_LIST_URL)
    
    # Obtener siguiente número de asiento
    ultimo_asiento = Asiento.objects.filter(empresa=empresa_activa).order_by('-numero_asiento').first()
    if ultimo_asiento and ultimo_asiento.numero_asiento.isdigit():
        nuevo_numero = str(int(ultimo_asiento.numero_asiento) + 1).zfill(6)
    else:
        nuevo_numero = '000001'
    
    # Crear nuevo asiento
    nuevo_asiento = Asiento.objects.create(
        empresa=empresa_activa,
        numero_asiento=nuevo_numero,
        fecha_asiento=timezone.now().date(),
        tipo_asiento=asiento_original.tipo_asiento,
        concepto=f'{asiento_original.concepto} (Duplicado)',
        observaciones=asiento_original.observaciones,
        estado='borrador',
        creado_por=request.user,
        total_debito=asiento_original.total_debito,
        total_credito=asiento_original.total_credito
    )
    
    # Copiar partidas
    for partida_original in asiento_original.partidas.all():
        Partida.objects.create(
            asiento=nuevo_asiento,
            cuenta=partida_original.cuenta,
            concepto=partida_original.concepto,
            valor_debito=partida_original.valor_debito,
            valor_credito=partida_original.valor_credito,
            orden=partida_original.orden
        )
    
    messages.success(request, f'Asiento duplicado exitosamente. Nuevo número: {nuevo_numero}')
    return redirect(ASIENTOS_DETALLE_URL, pk=nuevo_asiento.pk)

@login_required
@require_http_methods(["POST"])
def reversar_asiento(request, pk):
    """
    Reversa un asiento contable creando uno nuevo con débitos y créditos invertidos.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    asiento_original = get_object_or_404(Asiento, pk=pk)
    
    # Verificar permisos
    if empresa_activa and asiento_original.empresa != empresa_activa:
        messages.error(request, 'No tienes permiso para reversar este asiento.')
        return redirect(ASIENTOS_LIST_URL)
    
    # Verificar que esté confirmado
    if asiento_original.estado != 'confirmado':
        messages.error(request, 'Solo se pueden reversar asientos confirmados.')
        return redirect(ASIENTOS_DETALLE_URL, pk=pk)
    
    # Obtener siguiente número de asiento
    ultimo_asiento = Asiento.objects.filter(empresa=empresa_activa).order_by('-numero_asiento').first()
    if ultimo_asiento and ultimo_asiento.numero_asiento.isdigit():
        nuevo_numero = str(int(ultimo_asiento.numero_asiento) + 1).zfill(6)
    else:
        nuevo_numero = '000001'
    
    # Crear asiento de reversa
    asiento_reversa = Asiento.objects.create(
        empresa=empresa_activa,
        numero_asiento=nuevo_numero,
        fecha_asiento=timezone.now().date(),
        tipo_asiento='ajuste',
        concepto=f'REVERSA - {asiento_original.concepto}',
        observaciones=f'Reversa del asiento {asiento_original.numero_asiento}',
        estado='borrador',
        creado_por=request.user,
        total_debito=asiento_original.total_credito,  # Invertidos
        total_credito=asiento_original.total_debito   # Invertidos
    )
    
    # Copiar partidas invirtiendo débitos y créditos
    for partida_original in asiento_original.partidas.all():
        Partida.objects.create(
            asiento=asiento_reversa,
            cuenta=partida_original.cuenta,
            concepto=f'Reversa: {partida_original.concepto}',
            valor_debito=partida_original.valor_credito,  # Invertido
            valor_credito=partida_original.valor_debito,  # Invertido
            orden=partida_original.orden
        )
    
    messages.success(request, f'Asiento de reversa creado exitosamente. Nuevo número: {nuevo_numero}')
    return redirect(ASIENTOS_DETALLE_URL, pk=asiento_reversa.pk)

@login_required
@require_http_methods(["GET"])
def obtener_siguiente_numero_asiento(request):
    """
    Obtiene el siguiente número de asiento disponible para la empresa.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    if not empresa_activa:
        return JsonResponse({'error': 'No hay empresa activa'}, status=400)
    
    # Obtener el último asiento de la empresa
    ultimo_asiento = Asiento.objects.filter(empresa=empresa_activa).order_by('-numero_asiento').first()
    
    if ultimo_asiento and ultimo_asiento.numero_asiento.isdigit():
        nuevo_numero = str(int(ultimo_asiento.numero_asiento) + 1).zfill(6)
    else:
        nuevo_numero = '000001'
    
    return JsonResponse({
        'numero': nuevo_numero,
        'empresa': empresa_activa.razon_social
    })

@login_required
@require_http_methods(["GET"])
def buscar_cuentas(request):
    """
    Busca cuentas contables por código o nombre.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    query = request.GET.get('q', '')
    
    if not empresa_activa:
        return JsonResponse({'results': []}, status=400)
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Buscar cuentas
    cuentas = CuentaContable.objects.filter(
        empresa=empresa_activa,
        activa=True,
        acepta_movimiento=True
    ).filter(
        models.Q(codigo__icontains=query) | models.Q(nombre__icontains=query)
    ).order_by('codigo')[:20]
    
    results = []
    for cuenta in cuentas:
        results.append({
            'id': cuenta.pk,
            'codigo': cuenta.codigo,
            'nombre': cuenta.nombre,
            'tipo': cuenta.get_tipo_cuenta_display(),
            'naturaleza': cuenta.get_naturaleza_display(),
            'text': f'{cuenta.codigo} - {cuenta.nombre}'
        })
    
    return JsonResponse({'results': results})

@login_required
@require_http_methods(["POST"])
def validar_cuadre_asiento(request):
    """
    Valida que un asiento esté cuadrado (débitos = créditos).
    """
    from decimal import Decimal
    import json
    
    try:
        data = json.loads(request.body)
        total_debito = Decimal(str(data.get('total_debito', 0)))
        total_credito = Decimal(str(data.get('total_credito', 0)))
        
        diferencia = abs(total_debito - total_credito)
        cuadrado = diferencia < Decimal('0.01')
        
        return JsonResponse({
            'cuadrado': cuadrado,
            'total_debito': str(total_debito),
            'total_credito': str(total_credito),
            'diferencia': str(diferencia)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["GET"])
def obtener_saldo_cuenta(request, pk):
    """
    Obtiene el saldo actual de una cuenta contable.
    """
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    try:
        cuenta = CuentaContable.objects.get(pk=pk, empresa=empresa_activa)
        
        # Calcular saldo
        if cuenta.naturaleza == 'D':
            saldo = cuenta.saldo_debito - cuenta.saldo_credito
        else:
            saldo = cuenta.saldo_credito - cuenta.saldo_debito
        
        return JsonResponse({
            'id': cuenta.pk,
            'codigo': cuenta.codigo,
            'nombre': cuenta.nombre,
            'tipo': cuenta.get_tipo_cuenta_display(),
            'naturaleza': cuenta.get_naturaleza_display(),
            'saldo_debito': str(cuenta.saldo_debito),
            'saldo_credito': str(cuenta.saldo_credito),
            'saldo': str(saldo)
        })
    except CuentaContable.DoesNotExist:
        return JsonResponse({'error': 'Cuenta no encontrada'}, status=404)
