from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db.models import Prefetch, F, Sum, Value
from django.db.models.functions import Concat
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Factura, FacturaDetalle

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

class FacturaCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear una nueva factura.
    """
    model = Factura
    template_name = 'facturacion/crear.html'
    fields = [
        'cliente', 'fecha_factura', 'fecha_vencimiento', 'tipo_venta',
        'metodo_pago', 'observaciones'
    ]
    success_url = reverse_lazy('facturacion:lista')
    
    def get_initial(self):
        """
        Establece valores iniciales para el formulario.
        """
        initial = super().get_initial()
        initial['fecha_factura'] = timezone.now().date()
        return initial

    def form_valid(self, form):
        """
        Valida el formulario y asigna la empresa y número de factura.
        """
        try:
            # Obtener la empresa del usuario o lanzar excepción si no tiene
            if hasattr(self.request.user, 'empresa'):
                empresa = self.request.user.empresa
            else:
                raise ValueError("El usuario no tiene una empresa asignada.")
            
            # Asignar la empresa a la factura
            form.instance.empresa = empresa
            
            # Generar número de factura
            if not form.instance.numero_factura:
                ultima_factura = Factura.objects.filter(
                    empresa=empresa,
                    fecha_factura__year=timezone.now().year
                ).order_by('-numero_factura').first()
                
                if ultima_factura and ultima_factura.numero_factura:
                    try:
                        ultimo_numero = int(ultima_factura.numero_factura.split('-')[-1])
                        nuevo_numero = f"FACT-{timezone.now().year}{str(timezone.now().month).zfill(2)}-{str(ultimo_numero + 1).zfill(6)}"
                    except (IndexError, ValueError):
                        # Si hay un error al parsear el número, empezar desde 1
                        nuevo_numero = f"FACT-{timezone.now().year}{str(timezone.now().month).zfill(2)}-000001"
                else:
                    nuevo_numero = f"FACT-{timezone.now().year}{str(timezone.now().month).zfill(2)}-000001"
                
                form.instance.numero_factura = nuevo_numero
            
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
            messages.error(
                self.request,
                f'Error al crear la factura: {str(e)}'
            )
            return self.form_invalid(form)

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
