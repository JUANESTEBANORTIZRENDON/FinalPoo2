from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Prefetch, F, Sum, Q
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Factura, FacturaDetalle

# Decorador personalizado para verificar permisos de empresa
def empresa_required(view_func):
    """
    Verifica que el usuario tenga una empresa asignada.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not hasattr(request.user, 'empresa'):
            messages.error(request, 'No tiene una empresa asignada.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Vistas temporales básicas
class FacturaListView(LoginRequiredMixin, ListView):
    """
    Vista para listar facturas con paginación y optimizaciones de rendimiento.
    """
    model = Factura
    template_name = 'facturacion/lista.html'
    context_object_name = 'facturas'
    paginate_by = 20  # Número de facturas por página
    
    def get_queryset(self):
        """
        Optimiza las consultas para el listado de facturas.
        """
        cache_key = f'facturas_empresa_{self.request.user.empresa.id}'
        queryset = cache.get(cache_key)
        
        if not queryset:
            # Usamos select_related para las relaciones ForeignKey
            # y only() para seleccionar solo los campos necesarios
            queryset = Factura.objects.filter(
                empresa=self.request.user.empresa
            ).select_related(
                'cliente', 'metodo_pago'
            ).only(
                'id', 'numero_factura', 'fecha_factura', 'fecha_vencimiento',
                'tipo_venta', 'total', 'estado', 'cliente__razon_social',
                'metodo_pago__nombre'
            ).order_by('-fecha_factura', '-id')
            
            # Cacheamos los resultados por 5 minutos
            cache.set(cache_key, queryset, 300)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Agrega estadísticas y datos adicionales al contexto.
        """
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas (cacheadas por 5 minutos)
        cache_key = f'facturas_stats_{self.request.user.empresa.id}'
        stats = cache.get(cache_key)
        
        if not stats:
            queryset = self.get_queryset()
            
            stats = {
                'total_facturas': queryset.count(),
                'facturas_mes': queryset.filter(
                    fecha_factura__month=timezone.now().month,
                    fecha_factura__year=timezone.now().year
                ).count(),
                'total_ventas': queryset.aggregate(
                    total=Sum('total')
                )['total'] or 0
            }
            cache.set(cache_key, stats, 300)  # Cache por 5 minutos
        
        context.update({
            'title': 'Listado de Facturas',
            'stats': stats,
            'hoy': timezone.now().date(),
            'mes_actual': timezone.now().strftime('%B %Y')
        })
        
        return context

class FacturaDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada de una factura con optimización de consultas relacionadas.
    """
    model = Factura
    template_name = 'facturacion/detalle.html'
    context_object_name = 'factura'
    
    def get_queryset(self):
        """
        Optimiza las consultas para el detalle de la factura.
        """
        return Factura.objects.select_related(
            'cliente', 'metodo_pago'
        ).prefetch_related(
            Prefetch(
                'detalles',
                queryset=FacturaDetalle.objects.select_related('producto', 'impuesto')
            )
        ).only(
            'id', 'numero_factura', 'fecha_factura', 'fecha_vencimiento',
            'tipo_venta', 'subtotal', 'total_impuestos', 'total', 'observaciones',
            'cliente__razon_social', 'cliente__direccion', 'cliente__telefono',
            'cliente__email', 'metodo_pago__nombre', 'estado'
        )
    
    def get_context_data(self, **kwargs):
        """
        Agrega datos adicionales al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['title'] = f'Factura #{self.object.numero_factura}'
        return context

class EmpresaRequiredMixin(UserPassesTestMixin):
    """
    Mixin para verificar que el usuario tenga una empresa asignada.
    """
    def test_func(self):
        return hasattr(self.request.user, 'empresa')

    def handle_no_permission(self):
        messages.error(self.request, 'No tiene una empresa asignada.')
        return redirect('home')

class FacturaCreateView(LoginRequiredMixin, EmpresaRequiredMixin, CreateView):
    """
    Vista para crear una nueva factura con validaciones de seguridad.
    """
    model = Factura
    template_name = 'facturacion/crear.html'
    fields = [
        'cliente', 'fecha_factura', 'fecha_vencimiento', 'tipo_venta',
        'metodo_pago', 'observaciones'
    ]
    success_url = reverse_lazy('facturacion:lista')
    
    @method_decorator(csrf_protect)
    @method_decorator(transaction.atomic)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_initial(self):
        """
        Establece valores iniciales para el formulario.
        """
        initial = super().get_initial()
        initial['fecha_factura'] = timezone.now().date()
        return initial
        
    def get_form(self, form_class=None):
        """
        Filtra las opciones del formulario según la empresa del usuario.
        """
        form = super().get_form(form_class)
        empresa = self.request.user.empresa
        
        # Filtramos clientes y métodos de pago por empresa
        form.fields['cliente'].queryset = form.fields['cliente'].queryset.filter(
            empresa=empresa,
            activo=True
        )
        form.fields['metodo_pago'].queryset = form.fields['metodo_pago'].queryset.filter(
            empresa=empresa,
            activo=True
        )
        
        return form

    def form_valid(self, form):
        """
        Valida el formulario y asigna la empresa y número de factura.
        """
        try:
            with transaction.atomic():
                # Validar que el usuario tenga permiso para crear facturas
                if not self.request.user.has_perm('facturacion.add_factura'):
                    raise PermissionDenied('No tiene permiso para crear facturas')
                
                # Obtener la empresa del usuario
                empresa = self.request.user.empresa
                
                # Validar que el cliente pertenezca a la empresa
                cliente = form.cleaned_data.get('cliente')
                if cliente.empresa_id != empresa.id:
                    raise PermissionDenied('Operación no permitida')
                
                # Asignar la empresa a la factura
                form.instance.empresa = empresa
                
                # Generar número de factura de forma segura
                if not form.instance.numero_factura:
                    form.instance.numero_factura = self._generar_numero_factura(empresa)
                
                # Validar fechas
                if form.instance.fecha_vencimiento and form.instance.fecha_vencimiento < form.instance.fecha_factura:
                    form.add_error('fecha_vencimiento', 'La fecha de vencimiento debe ser posterior a la fecha de factura')
                    return self.form_invalid(form)
                
                # Guardar la factura
                response = super().form_valid(form)
                
                messages.success(
                    self.request,
                    'La factura se ha creado correctamente.'
                )
                return response
                
        except Exception as e:
            # Registro del error (en producción, usar logging)
            print(f"Error al crear factura: {str(e)}")
            messages.error(
                self.request,
                'Ocurrió un error al procesar la factura. Por favor, intente nuevamente.'
            )
            return self.form_invalid(form)
    
    def _generar_numero_factura(self, empresa):
        """
        Genera un número de factura único para la empresa.
        """
        with transaction.atomic():
            # Usamos select_for_update para evitar condiciones de carrera
            ultima_factura = Factura.objects.select_for_update().filter(
                empresa=empresa,
                fecha_factura__year=timezone.now().year
            ).order_by('-numero_factura').first()
            
            if ultima_factura and ultima_factura.numero_factura:
                try:
                    # Extraemos el número secuencial de la última factura
                    partes = ultima_factura.numero_factura.split('-')
                    if len(partes) >= 3 and partes[-1].isdigit():
                        ultimo_numero = int(partes[-1])
                        return f"FACT-{timezone.now().year}{timezone.now().month:02d}-{ultimo_numero + 1:06d}"
                except (ValueError, IndexError):
                    pass
            
            # Si no hay facturas o hay un error, comenzamos desde 1
            return f"FACT-{timezone.now().year}{timezone.now().month:02d}-{1:06d}"

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
@require_http_methods(["GET"])
@empresa_required
def factura_pdf(request, pk):
    """
    Vista para generar el PDF de una factura.
    """
    try:
        factura = get_object_or_404(
            Factura.objects.select_related('empresa'),
            pk=pk,
            empresa=request.user.empresa
        )
        
        # Aquí iría la generación del PDF
        # Por ahora, solo devolvemos una respuesta de ejemplo
        response = HttpResponse("PDF de la factura", content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="factura_{factura.numero_factura}.pdf"'
        return response
        
    except Exception as e:
        messages.error(request, 'No se pudo generar el PDF de la factura')
        return redirect('facturacion:detalle', pk=pk)

@login_required
def factura_imprimir(request, pk):
    return HttpResponse("Imprimir")

@login_required
@require_http_methods(["GET"])
@empresa_required
def exportar_facturas(request):
    """
    Vista para exportar facturas a formato Excel.
    """
    try:
        # Validar parámetros de fecha
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        
        # Validar formato de fechas
        try:
            if fecha_desde:
                fecha_desde = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
            if fecha_hasta:
                fecha_hasta = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Formato de fecha inválido. Use YYYY-MM-DD')
            return redirect('facturacion:lista')
        
        # Construir consulta con filtros
        facturas = Factura.objects.filter(empresa=request.user.empresa)
        
        if fecha_desde:
            facturas = facturas.filter(fecha_factura__gte=fecha_desde)
        if fecha_hasta:
            facturas = facturas.filter(fecha_factura__lte=fecha_hasta)
        
        # Aquí iría la generación del Excel
        # Por ahora, solo devolvemos una respuesta de ejemplo
        response = HttpResponse("Datos de exportación", content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=facturas_exportadas.xls'
        return response
        
    except Exception as e:
        messages.error(request, 'Error al exportar las facturas')
        return redirect('facturacion:lista')

@login_required
def obtener_siguiente_numero(request):
    return JsonResponse({'numero': '000001'})

@login_required
def calcular_totales_factura(request):
    return JsonResponse({'totales': {}})
