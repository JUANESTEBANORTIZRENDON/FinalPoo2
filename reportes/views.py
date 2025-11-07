from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_safe, require_POST
from django.http import JsonResponse, HttpResponse
from .models import ReporteGenerado, ConfiguracionReporte

# Vistas temporales básicas
class ReportesIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/index.html'

class LibroDiarioView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/diario.html'

class LibroMayorView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/mayor.html'

class LibroMayorCuentaView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/mayor_cuenta.html'

class BalanceComprobacionView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/balance_comprobacion.html'

class EstadoResultadosView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/estado_resultados.html'

class BalanceGeneralView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/balance_general.html'

class FlujoEfectivoView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/flujo_efectivo.html'

class ConfiguracionReporteListView(LoginRequiredMixin, ListView):
    model = ConfiguracionReporte
    template_name = 'reportes/configuraciones_lista.html'

class ConfiguracionReporteDetailView(LoginRequiredMixin, DetailView):
    model = ConfiguracionReporte
    template_name = 'reportes/configuraciones_detalle.html'

class ConfiguracionReporteCreateView(LoginRequiredMixin, CreateView):
    model = ConfiguracionReporte
    template_name = 'reportes/configuraciones_crear.html'
    fields = '__all__'

class ConfiguracionReporteUpdateView(LoginRequiredMixin, UpdateView):
    model = ConfiguracionReporte
    template_name = 'reportes/configuraciones_editar.html'
    fields = '__all__'

class ConfiguracionReporteDeleteView(LoginRequiredMixin, DeleteView):
    model = ConfiguracionReporte
    template_name = 'reportes/configuraciones_eliminar.html'

class ReporteGeneradoListView(LoginRequiredMixin, ListView):
    model = ReporteGenerado
    template_name = 'reportes/historial.html'

class ReporteGeneradoDetailView(LoginRequiredMixin, DetailView):
    model = ReporteGenerado
    template_name = 'reportes/historial_detalle.html'

@login_required
@require_safe
def generar_libro_diario(request):
    return redirect('reportes:diario')

@login_required
@require_http_methods(["GET"])
def exportar_libro_diario(request):
    return HttpResponse("CSV")

@login_required
@require_safe
def generar_libro_mayor(request):
    return redirect('reportes:mayor')

@login_required
@require_http_methods(["GET"])
def exportar_libro_mayor(request):
    return HttpResponse("CSV")

@login_required
@require_safe
def generar_balance_comprobacion(request):
    return redirect('reportes:balance_comprobacion')

@login_required
@require_http_methods(["GET"])
def exportar_balance_comprobacion(request):
    return HttpResponse("CSV")

@login_required
@require_safe
def generar_estado_resultados(request):
    return redirect('reportes:estado_resultados')

@login_required
@require_http_methods(["GET"])
def exportar_estado_resultados(request):
    return HttpResponse("CSV")

@login_required
@require_safe
def generar_balance_general(request):
    return redirect('reportes:balance_general')

@login_required
@require_http_methods(["GET"])
def exportar_balance_general(request):
    return HttpResponse("CSV")

@login_required
@require_safe
def generar_flujo_efectivo(request):
    return redirect('reportes:flujo_efectivo')

@login_required
@require_http_methods(["GET"])
def exportar_flujo_efectivo(request):
    return HttpResponse("CSV")

@login_required
@require_http_methods(["POST"])
def usar_configuracion(request, pk):
    return redirect('reportes:index')

@login_required
@require_http_methods(["GET"])
def descargar_reporte(request, pk):
    return HttpResponse("Archivo")

@login_required
@require_http_methods(["GET"])
def validar_periodo_reporte(request):
    return JsonResponse({'valido': True})

@login_required
@require_safe
def preview_reporte(request):
    return JsonResponse({'preview': {}})
