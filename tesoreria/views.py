from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone
from decimal import Decimal
import json
from .models import Pago, CuentaBancaria, PagoDetalle
from .forms import CobroForm
from .services import ServicioTesoreria
from facturacion.models import Factura
from catalogos.models import Producto, Tercero
from empresas.middleware import EmpresaFilterMixin
from contabilidad.asiento_helpers import (
    crear_asiento_ingreso,
    crear_asiento_egreso,
    anular_asiento_pago
)
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from core.constants import MSG_SELECCIONAR_EMPRESA, URL_CAMBIAR_EMPRESA

# Constantes específicas del módulo
URL_COBROS_LISTA = 'tesoreria:cobros_lista'
URL_CUENTAS_LISTA = 'tesoreria:cuentas_lista'
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todos los cobros (sin paginación) para estadísticas
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        if empresa_activa:
            todos_cobros = Pago.objects.filter(
                empresa=empresa_activa,
                tipo_pago='cobro'
            )
            
            # Filtrar por estado
            pendientes = todos_cobros.filter(estado='pendiente')
            activos = todos_cobros.filter(estado='activo')
            pagados = todos_cobros.filter(estado='pagado')
            
            # Calcular estadísticas con conteo y valor
            context['estadisticas'] = {
                'total_cobros': todos_cobros.count(),
                'valor_total': sum(cobro.valor for cobro in todos_cobros),
                'pendientes': pendientes.count(),
                'valor_pendientes': sum(cobro.valor for cobro in pendientes),
                'activos': activos.count(),
                'valor_activos': sum(cobro.valor for cobro in activos),
                'pagados': pagados.count(),
                'valor_pagados': sum(cobro.valor for cobro in pagados),
            }
        else:
            context['estadisticas'] = {
                'total_cobros': 0,
                'valor_total': 0,
                'pendientes': 0,
                'valor_pendientes': 0,
                'activos': 0,
                'valor_activos': 0,
                'pagados': 0,
                'valor_pagados': 0,
            }
        
        return context

class CobroCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Pago
    form_class = CobroForm
    template_name = 'tesoreria/cobros_crear.html'
    success_url = reverse_lazy(URL_COBROS_LISTA)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        # Obtener productos activos de la empresa
        if empresa_activa:
            productos = Producto.objects.filter(
                empresa=empresa_activa,
                activo=True
            ).values('id', 'nombre', 'precio_venta')
            
            # Convertir a JSON para JavaScript
            productos_list = [
                {
                    'id': p['id'],
                    'nombre': p['nombre'],
                    'precio': str(p['precio_venta'])
                }
                for p in productos
            ]
            context['productos_json'] = json.dumps(productos_list)
        else:
            context['productos_json'] = '[]'
        
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = getattr(self.request, 'empresa_activa', None)
        return kwargs
    
    def form_valid(self, form):
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        if not empresa_activa:
            messages.error(self.request, MSG_SELECCIONAR_EMPRESA)
            return redirect(URL_CAMBIAR_EMPRESA)
        
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
        form.instance.estado = 'pendiente'
        
        # Guardar el cobro primero
        response = super().form_valid(form)
        
        # Procesar los detalles de productos
        cobro = form.instance
        i = 0
        while f'producto_{i}' in self.request.POST:
            producto_id = self.request.POST.get(f'producto_{i}')
            cantidad = self.request.POST.get(f'cantidad_{i}')
            precio = self.request.POST.get(f'precio_{i}')
            
            if producto_id and cantidad and precio:
                try:
                    producto = Producto.objects.get(id=producto_id)
                    PagoDetalle.objects.create(
                        pago=cobro,
                        producto=producto,
                        cantidad=Decimal(cantidad),
                        precio_unitario=Decimal(precio)
                    )
                except (Producto.DoesNotExist, ValueError):  # type: ignore[misc]
                    # InvalidOperation es una excepción interna de Decimal
                    pass
            
            i += 1
        
        messages.success(
            self.request,
            f'Cobro {nuevo_numero} registrado exitosamente por ${form.instance.valor:,.2f}'
        )
        
        return response


class CobroUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = Pago
    form_class = CobroForm
    template_name = 'tesoreria/cobros_editar.html'
    success_url = reverse_lazy(URL_COBROS_LISTA)
    
    def get_queryset(self):
        # Solo permitir editar cobros en estado pendiente
        return super().get_queryset().filter(tipo_pago='cobro', estado='pendiente')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['empresa'] = getattr(self.request, 'empresa_activa', None)
        return kwargs
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'Cobro {form.instance.numero_pago} actualizado exitosamente'
        )
        return super().form_valid(form)

class CobroDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = Pago
    template_name = 'tesoreria/cobros_eliminar.html'
    success_url = reverse_lazy(URL_COBROS_LISTA)
    
    def get_queryset(self):
        # Solo permitir eliminar cobros
        return super().get_queryset().filter(tipo_pago='cobro')
    
    def delete(self, request, *args, **kwargs):
        cobro = self.get_object()
        messages.success(
            request,
            f'Cobro {cobro.numero_pago} eliminado exitosamente'
        )
        return super().delete(request, *args, **kwargs)

class IngresoListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Pago
    template_name = 'tesoreria/ingresos_lista.html'
    context_object_name = 'ingresos'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(tipo_pago='cobro')
        return queryset.select_related('tercero', 'empresa', 'metodo_pago', 'cuenta_bancaria').order_by('-fecha_pago')

class IngresoCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Pago
    template_name = 'tesoreria/ingresos_crear.html'
    fields = ['tercero', 'fecha_pago', 'valor', 'metodo_pago', 'cuenta_bancaria', 'referencia', 'observaciones']
    success_url = reverse_lazy('tesoreria:ingresos_lista')
    
    def form_valid(self, form):
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        form.instance.empresa = empresa_activa
        form.instance.tipo_pago = 'cobro'
        form.instance.creado_por = self.request.user
        form.instance.estado = 'pendiente'
        
        # Generar número consecutivo
        ultimo_ingreso = Pago.objects.filter(
            empresa=empresa_activa,
            tipo_pago='cobro',
            numero_pago__startswith='ING-'
        ).order_by('-numero_pago').first()
        
        if ultimo_ingreso and ultimo_ingreso.numero_pago:
            try:
                ultimo_num = int(ultimo_ingreso.numero_pago.split('-')[1])
                nuevo_numero = f'ING-{str(ultimo_num + 1).zfill(6)}'
            except (ValueError, AttributeError):
                nuevo_numero = 'ING-000001'
        else:
            nuevo_numero = 'ING-000001'
        
        form.instance.numero_pago = nuevo_numero
        
        # Guardar primero el ingreso
        response = super().form_valid(form)
        
        # Generar asiento contable automáticamente
        try:
            asiento = crear_asiento_ingreso(form.instance, self.request.user)
            messages.success(
                self.request,
                f'Ingreso {nuevo_numero} registrado exitosamente. '
                f'Asiento contable {asiento.numero_asiento} generado automáticamente.'
            )
        except ValueError as e:
            messages.warning(
                self.request,
                f'Ingreso {nuevo_numero} registrado, pero no se pudo generar el asiento contable: {str(e)}'
            )
        except Exception as e:
            messages.error(
                self.request,
                f'Ingreso {nuevo_numero} registrado, pero ocurrió un error al generar el asiento: {str(e)}'
            )
        
        return response

# ============================================================
# VISTAS PARA EGRESOS (PAGOS A PROVEEDORES)
# ============================================================

class EgresoListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = Pago
    template_name = 'tesoreria/egresos_lista.html'
    context_object_name = 'egresos'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(tipo_pago='egreso')
        return queryset.select_related('tercero', 'empresa', 'metodo_pago', 'cuenta_bancaria').order_by('-fecha_pago')

class EgresoCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = Pago
    template_name = 'tesoreria/egresos_crear.html'
    fields = ['tercero', 'fecha_pago', 'valor', 'metodo_pago', 'cuenta_bancaria', 'referencia', 'observaciones']
    success_url = reverse_lazy('tesoreria:egresos_lista')
    
    def form_valid(self, form):
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        form.instance.empresa = empresa_activa
        form.instance.tipo_pago = 'egreso'
        form.instance.creado_por = self.request.user
        form.instance.estado = 'pendiente'
        
        # Generar número consecutivo
        ultimo_egreso = Pago.objects.filter(
            empresa=empresa_activa,
            tipo_pago='egreso',
            numero_pago__startswith='EGR-'
        ).order_by('-numero_pago').first()
        
        if ultimo_egreso and ultimo_egreso.numero_pago:
            try:
                ultimo_num = int(ultimo_egreso.numero_pago.split('-')[1])
                nuevo_numero = f'EGR-{str(ultimo_num + 1).zfill(6)}'
            except (ValueError, AttributeError):
                nuevo_numero = 'EGR-000001'
        else:
            nuevo_numero = 'EGR-000001'
        
        form.instance.numero_pago = nuevo_numero
        
        # Descontar del saldo de la cuenta bancaria si hay cuenta seleccionada
        if form.instance.cuenta_bancaria:
            cuenta = form.instance.cuenta_bancaria
            if cuenta.saldo_actual >= form.instance.valor:
                cuenta.saldo_actual -= form.instance.valor
                cuenta.save()
            else:
                messages.warning(
                    self.request,
                    f'Advertencia: La cuenta {cuenta.nombre} tiene saldo insuficiente. '
                    f'Saldo: ${cuenta.saldo_actual:,.2f}, Egreso: ${form.instance.valor:,.2f}. '
                    f'El descuento se realizó de todas formas.'
                )
                cuenta.saldo_actual -= form.instance.valor
                cuenta.save()
        
        # Guardar primero el egreso
        response = super().form_valid(form)
        
        # Generar asiento contable automáticamente
        try:
            asiento = crear_asiento_egreso(form.instance, self.request.user)
            if form.instance.cuenta_bancaria:
                messages.success(
                    self.request,
                    f'Egreso {nuevo_numero} registrado exitosamente. '
                    f'Se descontaron ${form.instance.valor:,.2f} de {form.instance.cuenta_bancaria.nombre}. '
                    f'Asiento contable {asiento.numero_asiento} generado automáticamente.'
                )
            else:
                messages.success(
                    self.request,
                    f'Egreso {nuevo_numero} registrado exitosamente. '
                    f'Asiento contable {asiento.numero_asiento} generado automáticamente.'
                )
        except ValueError as e:
            messages.warning(
                self.request,
                f'Egreso {nuevo_numero} registrado, pero no se pudo generar el asiento contable: {str(e)}'
            )
        except Exception as e:
            messages.error(
                self.request,
                f'Egreso {nuevo_numero} registrado, pero ocurrió un error al generar el asiento: {str(e)}'
            )
        
        return response

class EgresoUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = Pago
    template_name = 'tesoreria/egresos_editar.html'
    fields = ['tercero', 'fecha_pago', 'valor', 'metodo_pago', 'cuenta_bancaria', 'referencia', 'observaciones']
    success_url = reverse_lazy('tesoreria:egresos_lista')
    
    def get_queryset(self):
        return super().get_queryset().filter(tipo_pago='egreso')
    
    def form_valid(self, form):
        egreso_original = self.get_object()
        
        # Si cambió la cuenta o el valor, ajustar saldos
        if egreso_original.cuenta_bancaria:
            # Devolver el monto a la cuenta original
            cuenta_original = egreso_original.cuenta_bancaria
            cuenta_original.saldo_actual += egreso_original.valor
            cuenta_original.save()
            
            # Descontar de la nueva cuenta si hay
            if form.instance.cuenta_bancaria:
                cuenta_nueva = form.instance.cuenta_bancaria
                cuenta_nueva.saldo_actual -= form.instance.valor
                cuenta_nueva.save()
                messages.success(
                    self.request,
                    f'Egreso {egreso_original.numero_pago} actualizado. '
                    f'Saldo ajustado: devuelto a {cuenta_original.nombre}, descontado de {cuenta_nueva.nombre}'
                )
            else:
                messages.success(
                    self.request,
                    f'Egreso {egreso_original.numero_pago} actualizado. '
                    f'Saldo de ${egreso_original.valor:,.2f} devuelto a {cuenta_original.nombre}'
                )
        else:
            # No tenía cuenta antes, pero ahora sí
            if form.instance.cuenta_bancaria:
                cuenta_nueva = form.instance.cuenta_bancaria
                cuenta_nueva.saldo_actual -= form.instance.valor
                cuenta_nueva.save()
                messages.success(
                    self.request,
                    f'Egreso {egreso_original.numero_pago} actualizado. '
                    f'Descontados ${form.instance.valor:,.2f} de {cuenta_nueva.nombre}'
                )
            else:
                messages.success(self.request, f'Egreso {egreso_original.numero_pago} actualizado exitosamente.')
        
        return super().form_valid(form)

class EgresoDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = Pago
    template_name = 'tesoreria/egresos_eliminar.html'
    success_url = reverse_lazy('tesoreria:egresos_lista')
    
    def get_queryset(self):
        return super().get_queryset().filter(tipo_pago='egreso')
    
    def delete(self, request, *args, **kwargs):
        egreso = self.get_object()
        
        # Devolver el monto a la cuenta bancaria si existe
        if egreso.cuenta_bancaria:
            cuenta = egreso.cuenta_bancaria
            cuenta.saldo_actual += egreso.valor
            cuenta.save()
        
        # Anular asiento contable si existe
        asiento_anulado = anular_asiento_pago(egreso)
        
        # Mensaje de confirmación
        if egreso.cuenta_bancaria:
            msg = f'Egreso {egreso.numero_pago} eliminado exitosamente. Saldo de ${egreso.valor:,.2f} devuelto a {egreso.cuenta_bancaria.nombre}'
        else:
            msg = f'Egreso {egreso.numero_pago} eliminado exitosamente.'
        
        if asiento_anulado:
            msg += f' Asiento contable {egreso.asiento_contable.numero_asiento} anulado.'
        
        messages.success(request, msg)
        return super().delete(request, *args, **kwargs)

class CuentaBancariaListView(LoginRequiredMixin, EmpresaFilterMixin, ListView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_lista.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('empresa', 'cuenta_contable').order_by('nombre')

class CuentaBancariaDetailView(LoginRequiredMixin, EmpresaFilterMixin, DetailView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_detalle.html'

class CuentaBancariaCreateView(LoginRequiredMixin, EmpresaFilterMixin, CreateView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_crear.html'
    fields = ['codigo', 'nombre', 'tipo_cuenta', 'numero_cuenta', 'banco', 'saldo_actual', 'cuenta_contable', 'activa']
    success_url = reverse_lazy(URL_CUENTAS_LISTA)
    
    def form_valid(self, form):
        form.instance.empresa = getattr(self.request, 'empresa_activa', None)
        messages.success(self.request, f'Cuenta bancaria {form.instance.nombre} creada exitosamente.')
        return super().form_valid(form)

class CuentaBancariaUpdateView(LoginRequiredMixin, EmpresaFilterMixin, UpdateView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_editar.html'
    fields = ['codigo', 'nombre', 'tipo_cuenta', 'numero_cuenta', 'banco', 'saldo_actual', 'cuenta_contable', 'activa']
    success_url = reverse_lazy(URL_CUENTAS_LISTA)
    
    def form_valid(self, form):
        messages.success(self.request, f'Cuenta bancaria {form.instance.nombre} actualizada exitosamente.')
        return super().form_valid(form)

class CuentaBancariaDeleteView(LoginRequiredMixin, EmpresaFilterMixin, DeleteView):
    model = CuentaBancaria
    template_name = 'tesoreria/cuentas_eliminar.html'
    success_url = reverse_lazy(URL_CUENTAS_LISTA)
    
    def delete(self, request, *args, **kwargs):
        cuenta = self.get_object()
        messages.success(request, f'Cuenta bancaria {cuenta.nombre} eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)

class FlujoCajaView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/flujo_caja.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        if not empresa_activa:
            return context
        
        # Obtener parámetros de filtro
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        cuenta_id = self.request.GET.get('cuenta')
        
        # Base queryset: solo pagos pagados de la empresa activa
        movimientos = Pago.objects.filter(
            empresa=empresa_activa,
            estado='pagado'
        ).select_related('tercero', 'cuenta_bancaria', 'metodo_pago')
        
        # Aplicar filtros
        if fecha_inicio:
            movimientos = movimientos.filter(fecha_pago__gte=fecha_inicio)
            context['fecha_inicio'] = fecha_inicio
        
        if fecha_fin:
            movimientos = movimientos.filter(fecha_pago__lte=fecha_fin)
            context['fecha_fin'] = fecha_fin
        
        if cuenta_id:
            movimientos = movimientos.filter(cuenta_bancaria_id=cuenta_id)
            context['cuenta_id'] = cuenta_id
        
        # Ordenar por fecha
        movimientos = movimientos.order_by('fecha_pago', 'id')
        
        # Calcular totales
        total_ingresos = movimientos.filter(tipo_pago='cobro').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
        
        total_egresos = movimientos.filter(tipo_pago='egreso').aggregate(
            total=models.Sum('valor')
        )['total'] or 0
        
        count_ingresos = movimientos.filter(tipo_pago='cobro').count()
        count_egresos = movimientos.filter(tipo_pago='egreso').count()
        
        flujo_neto = total_ingresos - total_egresos
        
        # Calcular saldo acumulado para cada movimiento
        saldo_acumulado = 0
        movimientos_con_saldo = []
        for mov in movimientos:
            if mov.tipo_pago == 'cobro':
                saldo_acumulado += mov.valor
            else:
                saldo_acumulado -= mov.valor
            mov.saldo_acumulado = saldo_acumulado
            movimientos_con_saldo.append(mov)
        
        # Obtener todas las cuentas bancarias para el filtro
        cuentas = CuentaBancaria.objects.filter(
            empresa=empresa_activa,
            activo=True
        ).order_by('nombre_banco')
        
        context.update({
            'movimientos': movimientos_con_saldo,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'count_ingresos': count_ingresos,
            'count_egresos': count_egresos,
            'flujo_neto': flujo_neto,
            'cuentas': cuentas,
        })
        
        return context

class SaldosCuentasView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/saldos_cuentas.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        if not empresa_activa:
            return context
        
        # Obtener todas las cuentas bancarias activas
        cuentas = CuentaBancaria.objects.filter(
            empresa=empresa_activa,
            activo=True
        ).order_by('nombre_banco')
        
        cuentas_con_saldo = []
        saldo_total = 0
        
        for cuenta in cuentas:
            # Calcular ingresos (cobros)
            ingresos = Pago.objects.filter(
                empresa=empresa_activa,
                cuenta_bancaria=cuenta,
                tipo_pago='cobro',
                estado='pagado'
            ).aggregate(total=models.Sum('valor'))['total'] or 0
            
            # Calcular egresos
            egresos = Pago.objects.filter(
                empresa=empresa_activa,
                cuenta_bancaria=cuenta,
                tipo_pago='egreso',
                estado='pagado'
            ).aggregate(total=models.Sum('valor'))['total'] or 0
            
            # Saldo de la cuenta
            saldo_cuenta = cuenta.saldo_inicial + ingresos - egresos
            saldo_total += saldo_cuenta
            
            cuentas_con_saldo.append({
                'cuenta': cuenta,
                'ingresos': ingresos,
                'egresos': egresos,
                'saldo': saldo_cuenta,
            })
        
        context.update({
            'cuentas_con_saldo': cuentas_con_saldo,
            'saldo_total': saldo_total,
        })
        
        return context

class PagosPeriodoView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/pagos_periodo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        empresa_activa = getattr(self.request, 'empresa_activa', None)
        
        if not empresa_activa:
            return context
        
        # Obtener parámetros de filtro
        fecha_inicio = self.request.GET.get('fecha_inicio')
        fecha_fin = self.request.GET.get('fecha_fin')
        tipo_pago = self.request.GET.get('tipo_pago', '')
        estado = self.request.GET.get('estado', '')
        
        # Base queryset
        pagos = Pago.objects.filter(
            empresa=empresa_activa
        ).select_related('tercero', 'cuenta_bancaria', 'metodo_pago')
        
        # Aplicar filtros
        if fecha_inicio:
            pagos = pagos.filter(fecha_pago__gte=fecha_inicio)
            context['fecha_inicio'] = fecha_inicio
        
        if fecha_fin:
            pagos = pagos.filter(fecha_pago__lte=fecha_fin)
            context['fecha_fin'] = fecha_fin
        
        if tipo_pago:
            pagos = pagos.filter(tipo_pago=tipo_pago)
            context['tipo_pago'] = tipo_pago
        
        if estado:
            pagos = pagos.filter(estado=estado)
            context['estado'] = estado
        
        # Ordenar por fecha descendente
        pagos = pagos.order_by('-fecha_pago', '-id')
        
        # Calcular totales
        total_pagos = pagos.aggregate(total=models.Sum('valor'))['total'] or 0
        count_pagos = pagos.count()
        
        context.update({
            'pagos': pagos[:100],  # Limitar a 100 registros
            'total_pagos': total_pagos,
            'count_pagos': count_pagos,
        })
        
        return context

@login_required
@require_http_methods(["POST"])
def activar_cobro(request, pk):
    """
    Activa un cobro (cambia estado a activo) y genera una factura automáticamente.
    """
    cobro = get_object_or_404(Pago, pk=pk, tipo_pago='cobro')
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    if not empresa_activa:
        messages.error(request, MSG_SELECCIONAR_EMPRESA)
        return redirect(URL_CAMBIAR_EMPRESA)
    
    # Verificar que el cobro esté en pendiente
    if cobro.estado != 'pendiente':
        messages.error(request, 'Solo se pueden activar cobros en estado pendiente.')
        return redirect(URL_COBROS_LISTA)
    
    # Generar número de factura automático
    ultima_factura = Factura.objects.filter(
        empresa=empresa_activa
    ).order_by('-numero_factura').first()
    
    if ultima_factura:
        try:
            ultimo_numero = int(ultima_factura.numero_factura.replace('FAC-', ''))
            nuevo_numero = f'FAC-{(ultimo_numero + 1):06d}'
        except (ValueError, AttributeError):
            nuevo_numero = 'FAC-000001'
    else:
        nuevo_numero = 'FAC-000001'
    
    # Crear la factura con toda la información del cobro
    factura = Factura.objects.create(
        empresa=empresa_activa,
        numero_factura=nuevo_numero,
        fecha_factura=cobro.fecha_pago,
        cliente=cobro.tercero,
        tipo_venta='contado',
        metodo_pago=cobro.metodo_pago,
        subtotal=cobro.valor,
        total_impuestos=Decimal('0.00'),
        total=cobro.valor,
        estado='confirmada',
        observaciones=f'Factura generada desde cobro {cobro.numero_pago}.\n'
                     f'Cliente: {cobro.tercero.razon_social}\n'
                     f'Documento: {cobro.tercero.numero_documento}\n'
                     f'Método de pago: {cobro.metodo_pago.nombre}\n'
                     f'Referencia: {cobro.referencia or "N/A"}\n'
                     f'Observaciones del cobro: {cobro.observaciones or "N/A"}',
        creado_por=request.user,
        confirmado_por=request.user,
        fecha_confirmacion=timezone.now()
    )
    
    # Actualizar el cobro a estado activo
    cobro.estado = 'activo'
    cobro.confirmado_por = request.user
    cobro.fecha_confirmacion = timezone.now()
    cobro.factura = factura  # type: ignore[assignment]
    cobro.save()
    
    messages.success(
        request,
        f'Cobro {cobro.numero_pago} activado exitosamente. Factura {nuevo_numero} generada.'
    )
    
    return redirect(URL_COBROS_LISTA)


def _construir_info_pago_efectivo(request):
    """Construye la información de pago en efectivo."""
    monto_recibido = request.POST.get('monto_recibido', '0')
    cambio = request.POST.get('cambio', '0')
    return f"Pago en efectivo - Recibido: ${monto_recibido} - Cambio: ${cambio}"


def _construir_info_pago_transferencia(request):
    """Construye la información de pago por transferencia."""
    cuenta_origen = request.POST.get('cuenta_origen', 'N/A')
    descripcion = request.POST.get('descripcion', '')
    monto_transferencia = request.POST.get('monto_transferencia', '0')
    
    info_pago = "Pago por transferencia bancaria\n"
    info_pago += f"Cuenta Origen: {cuenta_origen}\n"
    info_pago += "Cuenta Destino: 1234-5678-9012 (Bancolombia)\n"
    info_pago += f"Monto: ${monto_transferencia}"
    
    if descripcion:
        info_pago += f"\nDescripción: {descripcion}"
    
    return info_pago


def _agregar_observacion(objeto, nueva_info):
    """Agrega información a las observaciones de un objeto."""
    if objeto.observaciones:
        objeto.observaciones += f"\n{nueva_info}"
    else:
        objeto.observaciones = nueva_info


def _actualizar_info_pago(cobro, metodo_pago, request):
    """Actualiza la información del pago en el cobro y factura asociada."""
    # Construir información según método de pago
    if metodo_pago == 'efectivo':
        info_pago = _construir_info_pago_efectivo(request)
    elif metodo_pago == 'transferencia':
        info_pago = _construir_info_pago_transferencia(request)
    else:
        info_pago = f"Pago con método: {metodo_pago}"
    
    # Actualizar observaciones del cobro
    _agregar_observacion(cobro, info_pago)
    
    # Actualizar factura si existe
    if cobro.factura:
        info_factura = info_pago.replace("Pago ", "Pagado ")
        _agregar_observacion(cobro.factura, info_factura)
        cobro.factura.estado = 'pagada'
        cobro.factura.save()


@login_required
@require_http_methods(["POST"])
def marcar_cobro_pagado(request, pk):
    """
    Marca un cobro activo como pagado y actualiza el estado de la factura asociada.
    Guarda información del pago (método, monto recibido, cambio).
    """
    cobro = get_object_or_404(Pago, pk=pk, tipo_pago='cobro')
    
    if cobro.estado != 'activo':
        messages.error(request, 'Solo se pueden marcar como pagados los cobros activos.')
        return redirect(URL_COBROS_LISTA)
    
    # Obtener método de pago
    metodo_pago = request.POST.get('metodo_pago', 'efectivo')
    
    # Actualizar estado del cobro
    cobro.estado = 'pagado'
    
    # Actualizar información de pago
    _actualizar_info_pago(cobro, metodo_pago, request)
    
    # Guardar cobro
    cobro.save()
    
    # Mensaje de éxito
    if cobro.factura:
        messages.success(
            request, 
            f'✓ Pago procesado exitosamente\nCobro: {cobro.numero_pago}\nFactura: {cobro.factura.numero_factura}\nMétodo: {metodo_pago.capitalize()}'
        )
    else:
        messages.success(request, f'Cobro {cobro.numero_pago} marcado como pagado.')
    
    return redirect(URL_COBROS_LISTA)


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


@login_required
@require_http_methods(["GET"])
def generar_factura_pdf(request, factura_pk):
    """
    Genera un PDF de la factura con el formato: CODIGO_NOMBRECLIENTE.pdf
    """
    factura = get_object_or_404(Factura, pk=factura_pk)
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    # Verificar que la factura pertenezca a la empresa activa
    if factura.empresa != empresa_activa:
        messages.error(request, 'No tienes permiso para ver esta factura.')
        return redirect('facturacion:facturas_lista')
    
    # Crear el nombre del archivo
    nombre_cliente = factura.cliente.razon_social.replace(' ', '_').replace('/', '_')
    nombre_archivo = f"{factura.numero_factura}_{nombre_cliente}.pdf"
    
    # Crear el PDF en memoria
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    elements.append(Paragraph("FACTURA DE VENTA", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de la empresa
    empresa_data = [
        ['EMPRESA:', factura.empresa.razon_social],
        ['NIT:', factura.empresa.nit],
        ['Dirección:', factura.empresa.direccion or 'N/A'],
        ['Teléfono:', factura.empresa.telefono or 'N/A'],
    ]
    
    empresa_table = Table(empresa_data, colWidths=[2*inch, 4*inch])
    empresa_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(empresa_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información de la factura
    factura_data = [
        ['FACTURA N°:', factura.numero_factura],
        ['FECHA:', factura.fecha_factura.strftime('%d/%m/%Y')],
        ['TIPO VENTA:', factura.get_tipo_venta_display()],  # type: ignore[attr-defined]
        ['ESTADO:', factura.get_estado_display()],  # type: ignore[attr-defined]
    ]
    
    factura_table = Table(factura_data, colWidths=[2*inch, 4*inch])
    factura_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(factura_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Información del cliente
    cliente_data = [
        ['CLIENTE:', factura.cliente.razon_social],
        ['DOCUMENTO:', f"{factura.cliente.get_tipo_documento_display()}: {factura.cliente.numero_documento}"],
        ['Dirección:', factura.cliente.direccion or 'N/A'],
        ['Teléfono:', factura.cliente.telefono or 'N/A'],
        ['Email:', factura.cliente.email or 'N/A'],
    ]
    
    cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
    cliente_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(cliente_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Totales
    totales_data = [
        ['SUBTOTAL:', f"${factura.subtotal:,.2f}"],
        ['IMPUESTOS:', f"${factura.total_impuestos:,.2f}"],
        ['TOTAL:', f"${factura.total:,.2f}"],
    ]
    
    totales_table = Table(totales_data, colWidths=[4*inch, 2*inch])
    totales_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -2), colors.HexColor('#ecf0f1')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, -2), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -2), 11),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(totales_table)
    
    # Observaciones
    if factura.observaciones:
        elements.append(Spacer(1, 0.3*inch))
        elements.append(Paragraph(f"<b>Observaciones:</b> {factura.observaciones}", styles['Normal']))
    
    # Construir el PDF
    doc.build(elements)
    
    # Obtener el valor del buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Crear la respuesta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    response.write(pdf)
    
    return response


@login_required
@require_http_methods(["POST"])
def crear_cliente_ajax(request):
    """
    Crea un nuevo cliente (tercero) vía AJAX desde el formulario de cobros.
    El cliente se crea como tipo 'cliente' y estado 'activo' automáticamente.
    """
    try:
        empresa_activa = getattr(request, 'empresa_activa', None)
        
        if not empresa_activa:
            return JsonResponse({
                'success': False,
                'error': MSG_SELECCIONAR_EMPRESA
            }, status=400)
        
        # Obtener datos del formulario
        tipo_documento = request.POST.get('tipo_documento')
        numero_documento = request.POST.get('numero_documento')
        razon_social = request.POST.get('razon_social')
        telefono = request.POST.get('telefono', '')
        email = request.POST.get('email', '')
        direccion = request.POST.get('direccion', '')
        
        # Validar campos requeridos
        if not tipo_documento or not numero_documento or not razon_social:
            return JsonResponse({
                'success': False,
                'error': 'Los campos Tipo de Documento, Número de Documento y Razón Social son obligatorios.'
            }, status=400)
        
        # Verificar si ya existe un tercero con ese documento en la misma empresa
        if Tercero.objects.filter(
            empresa=empresa_activa,
            numero_documento=numero_documento
        ).exists():
            return JsonResponse({
                'success': False,
                'error': f'Ya existe un tercero registrado con el documento {numero_documento} en tu empresa.'
            }, status=400)
        
        # Crear el nuevo cliente
        cliente = Tercero.objects.create(
            empresa=empresa_activa,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            razon_social=razon_social,
            nombre_comercial='',
            telefono=telefono if telefono else '',
            email=email if email else '',
            direccion=direccion if direccion else '',
            ciudad='',
            departamento='',
            tipo_tercero='cliente',  # Automáticamente como cliente
            activo=True  # Automáticamente activo
        )
        
        # Retornar respuesta exitosa con formato para el dropdown
        display_text = f"{cliente.razon_social} ({cliente.numero_documento})"
        
        return JsonResponse({
            'success': True,
            'cliente': {
                'id': cliente.id,  # type: ignore[attr-defined]
                'razon_social': cliente.razon_social,
                'numero_documento': cliente.numero_documento,
                'tipo_documento': cliente.get_tipo_documento_display(),  # type: ignore[attr-defined]
                'display_text': display_text
            },
            'message': f'Cliente {cliente.razon_social} registrado exitosamente.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear el cliente: {str(e)}'
        }, status=500)


from django.views.generic import TemplateView
from django.db.models import Sum, Count, Q
from django.utils.dateparse import parse_date
from django.http import HttpResponse
import csv

class PagosReporteView(LoginRequiredMixin, TemplateView):
    template_name = 'tesoreria/pagos_reporte.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = Pago.objects.all()
        empresa = getattr(self.request, 'empresa_activa', None)
        if empresa:
            qs = qs.filter(empresa=empresa)

        fecha_desde = self.request.GET.get('desde')
        fecha_hasta = self.request.GET.get('hasta')
        tipo = self.request.GET.get('tipo')
        estado = self.request.GET.get('estado')

        if fecha_desde:
            qs = qs.filter(fecha__date__gte=parse_date(fecha_desde))
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=parse_date(fecha_hasta))
        if tipo in dict(Pago.TIPO_PAGO_CHOICES):
            qs = qs.filter(tipo=tipo)
        if estado in dict(Pago.ESTADO_CHOICES):
            qs = qs.filter(estado=estado)

        agregados = qs.aggregate(
            total_valor=Sum('valor'),
            total_registros=Count('id'),
            total_pendientes=Count('id', filter=Q(estado='pendiente')),
            total_aprobados=Count('id', filter=Q(estado='aprobado')),
            total_anulados=Count('id', filter=Q(estado='anulado')),
        )
        ctx['pagos'] = qs.select_related('empresa', 'cliente')
        ctx['agregados'] = agregados
        return ctx

@login_required
@require_http_methods(["GET"])
def pagos_reporte_csv(request):
    """
    Genera reporte CSV de pagos con filtros opcionales.
    
    Security Note: Esta vista usa método GET para operación de solo lectura (exportación).
    No requiere protección CSRF adicional ya que no modifica estado del servidor.
    Cumple con RFC 7231 (métodos seguros HTTP) y mejores prácticas de Django.
    El decorador @require_http_methods(["GET"]) hace explícito que solo acepta GET.
    """
    qs = Pago.objects.all()
    empresa = getattr(request, 'empresa_activa', None)
    if empresa:
        qs = qs.filter(empresa=empresa)

    fecha_desde = request.GET.get('desde')
    fecha_hasta = request.GET.get('hasta')
    tipo = request.GET.get('tipo')
    estado = request.GET.get('estado')

    if fecha_desde:
        qs = qs.filter(fecha__date__gte=parse_date(fecha_desde))
    if fecha_hasta:
        qs = qs.filter(fecha__date__lte=parse_date(fecha_hasta))
    if tipo in dict(Pago.TIPO_PAGO_CHOICES):
        qs = qs.filter(tipo=tipo)
    if estado in dict(Pago.ESTADO_CHOICES):
        qs = qs.filter(estado=estado)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_pagos.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Tipo', 'Estado', 'Cliente', 'Valor'])
    for p in qs.select_related('cliente'):
        writer.writerow([p.id, getattr(p, 'fecha', ''), p.tipo, p.estado, getattr(p.cliente, 'razon_social', ''), p.valor])
    return response


@login_required
@require_http_methods(["POST"])
def enviar_factura_email(request, factura_pk):
    factura = get_object_or_404(Factura, pk=factura_pk)
    empresa_activa = getattr(request, 'empresa_activa', None)
    if factura.empresa != empresa_activa:
        messages.error(request, 'No tienes permiso para enviar esta factura.')
        return redirect('facturacion:facturas_lista')

    # Reusar PDF generado por la vista existente
    response = generar_factura_pdf(request, factura_pk)
    if getattr(response, 'status_code', 500) != 200 or response.get('Content-Type') != 'application/pdf':
        messages.error(request, 'No fue posible generar el PDF.')
        return redirect('facturacion:facturas_detalle', pk=factura_pk)

    pdf_bytes = response.content
    from .services.emailing import send_invoice_email
    destinatario = getattr(factura.cliente, 'email', None)
    try:
        send_invoice_email(factura, pdf_bytes, destinatario)
        messages.success(request, 'Factura enviada correctamente.')
    except Exception as e:
        messages.error(request, f'Error enviando email: {e}')
    return redirect('facturacion:facturas_detalle', pk=factura_pk)


# ========== VISTAS DE ACCIONES DE TESORERÍA ==========

@login_required
@require_http_methods(["POST"])
def confirmar_pago(request, pk):
    """
    Confirma un pago pendiente.
    """
    pago = get_object_or_404(Pago, pk=pk, empresa=request.empresa_activa)
    
    success, message = ServicioTesoreria.confirmar_pago(pago, request.user)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect(PAGOS_DETALLE_URL, pk=pk)


@login_required
@require_http_methods(["POST"])
def anular_pago(request, pk):
    """
    Anula un pago.
    """
    pago = get_object_or_404(Pago, pk=pk, empresa=request.empresa_activa)
    motivo = request.POST.get('motivo', '')
    
    success, message = ServicioTesoreria.anular_pago(pago, motivo)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect(PAGOS_DETALLE_URL, pk=pk)


@login_required
@require_http_methods(["POST"])
def marcar_pago_pagado(request, pk):
    """
    Marca un pago como pagado.
    """
    pago = get_object_or_404(Pago, pk=pk, empresa=request.empresa_activa)
    
    success, message = ServicioTesoreria.marcar_pago_como_pagado(pago, request.user)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect(PAGOS_DETALLE_URL, pk=pk)
