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
from facturacion.models import Factura
from catalogos.models import Producto, Tercero
from empresas.middleware import EmpresaFilterMixin
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

# Constantes para evitar duplicación de literales
URL_COBROS_LISTA = 'tesoreria:cobros_lista'
CAMBIAR_EMPRESA_URL = 'empresas:cambiar_empresa'
MSG_SELECCIONAR_EMPRESA = 'Debes seleccionar una empresa.'
CAMBIAR_EMPRESA_URL = 'empresas:cambiar_empresa'

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
            return redirect(CAMBIAR_EMPRESA_URL)
        
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
                except (Producto.DoesNotExist, ValueError, Decimal.InvalidOperation):
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
def activar_cobro(request, pk):
    """
    Activa un cobro (cambia estado a activo) y genera una factura automáticamente.
    """
    cobro = get_object_or_404(Pago, pk=pk, tipo_pago='cobro')
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    if not empresa_activa:
        messages.error(request, MSG_SELECCIONAR_EMPRESA)
        return redirect(CAMBIAR_EMPRESA_URL)
    
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
    cobro.factura = factura
    cobro.save()
    
    messages.success(
        request,
        f'Cobro {cobro.numero_pago} activado exitosamente. Factura {nuevo_numero} generada.'
    )
    
    return redirect(URL_COBROS_LISTA)


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
    
    # Obtener datos del pago
    metodo_pago = request.POST.get('metodo_pago', 'efectivo')
    
    # Actualizar el cobro
    cobro.estado = 'pagado'
    
    # Guardar información del pago en observaciones según el método
    if metodo_pago == 'efectivo':
        monto_recibido = request.POST.get('monto_recibido', '0')
        cambio = request.POST.get('cambio', '0')
        info_pago = f"Pago en efectivo - Recibido: ${monto_recibido} - Cambio: ${cambio}"
        
        if cobro.observaciones:
            cobro.observaciones += f"\n{info_pago}"
        else:
            cobro.observaciones = info_pago
            
    elif metodo_pago == 'transferencia':
        cuenta_origen = request.POST.get('cuenta_origen', 'N/A')
        descripcion = request.POST.get('descripcion', '')
        monto_transferencia = request.POST.get('monto_transferencia', '0')
        
        info_pago = "Pago por transferencia bancaria\n"
        info_pago += f"Cuenta Origen: {cuenta_origen}\n"
        info_pago += "Cuenta Destino: 1234-5678-9012 (Bancolombia)\n"
        info_pago += f"Monto: ${monto_transferencia}"
        if descripcion:
            info_pago += f"\nDescripción: {descripcion}"
        
        if cobro.observaciones:
            cobro.observaciones += f"\n{info_pago}"
        else:
            cobro.observaciones = info_pago
    
    cobro.save()
    
    # Actualizar la factura asociada si existe
    if cobro.factura:
        cobro.factura.estado = 'pagada'
        
        # Agregar información de pago a la factura
        if metodo_pago == 'efectivo':
            monto_recibido = request.POST.get('monto_recibido', '0')
            cambio = request.POST.get('cambio', '0')
            info_factura = f"Pagado en efectivo - Recibido: ${monto_recibido} - Cambio: ${cambio}"
            
            if cobro.factura.observaciones:
                cobro.factura.observaciones += f"\n{info_factura}"
            else:
                cobro.factura.observaciones = info_factura
                
        elif metodo_pago == 'transferencia':
            cuenta_origen = request.POST.get('cuenta_origen', 'N/A')
            descripcion = request.POST.get('descripcion', '')
            monto_transferencia = request.POST.get('monto_transferencia', '0')
            
            info_factura = "Pagado por transferencia bancaria\n"
            info_factura += f"Cuenta Origen: {cuenta_origen}\n"
            info_factura += f"Monto: ${monto_transferencia}"
            if descripcion:
                info_factura += f"\nDescripción: {descripcion}"
            
            if cobro.factura.observaciones:
                cobro.factura.observaciones += f"\n{info_factura}"
            else:
                cobro.factura.observaciones = info_factura
        
        cobro.factura.save()
        
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
        ['TIPO VENTA:', factura.get_tipo_venta_display()],
        ['ESTADO:', factura.get_estado_display()],
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
        
        # Verificar si ya existe un tercero con ese documento
        if Tercero.objects.filter(numero_documento=numero_documento).exists():
            return JsonResponse({
                'success': False,
                'error': f'Ya existe un tercero registrado con el documento {numero_documento}.'
            }, status=400)
        
        # Crear el nuevo cliente
        cliente = Tercero.objects.create(
            empresa=empresa_activa,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            razon_social=razon_social,
            telefono=telefono if telefono else '',
            email=email if email else '',
            direccion=direccion if direccion else '',
            tipo_tercero='cliente',  # Automáticamente como cliente
            activo=True  # Automáticamente activo
        )
        
        # Retornar respuesta exitosa
        return JsonResponse({
            'success': True,
            'cliente': {
                'id': cliente.id,
                'razon_social': cliente.razon_social,
                'numero_documento': cliente.numero_documento,
                'tipo_documento': cliente.get_tipo_documento_display()
            },
            'message': f'Cliente {cliente.razon_social} registrado exitosamente.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear el cliente: {str(e)}'
        }, status=500)
