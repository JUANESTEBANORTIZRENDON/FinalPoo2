from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Empresa, PerfilEmpresa, HistorialCambios
from facturacion.models import Factura
from tesoreria.models import Pago
from contabilidad.models import Asiento

def es_contador(user, empresa_id=None):
    """
    Verifica si el usuario tiene rol de contador en alguna empresa o en una específica
    """
    if empresa_id:
        return PerfilEmpresa.objects.filter(
            usuario=user,
            empresa_id=empresa_id,
            rol='contador',
            activo=True
        ).exists()
    return PerfilEmpresa.objects.filter(
        usuario=user,
        rol='contador',
        activo=True
    ).exists()

@login_required
@require_http_methods(["GET"])
def contador_dashboard(request):
    """
    Dashboard principal del contador
    """
    # Verificar si el usuario tiene rol de contador en alguna empresa
    if not es_contador(request.user):
        messages.error(request, 'No tienes permisos para acceder al dashboard de contador.')
        return redirect('core:home')
    
    # Obtener las empresas donde el usuario es contador
    empresas_contador = Empresa.objects.filter(
        perfiles__usuario=request.user,
        perfiles__rol='contador',
        perfiles__activo=True
    ).distinct()
    
    # Si solo tiene una empresa, redirigir directamente al dashboard de esa empresa
    if empresas_contador.count() == 1:
        return redirect('empresas:contador_dashboard_empresa', empresa_id=empresas_contador.first().id)
    
    context = {
        'empresas': empresas_contador,
        'titulo': 'Seleccionar Empresa',
    }
    
    return render(request, 'empresas/contador/contador_dashboard.html', context)

@login_required
@require_http_methods(["GET"])
def contador_dashboard_empresa(request, empresa_id):
    """
    Dashboard del contador para una empresa específica
    """
    # Verificar permisos
    if not es_contador(request.user, empresa_id):
        messages.error(request, 'No tienes permisos para acceder a esta empresa.')
        return redirect('empresas:contador_dashboard')
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # Obtener estadísticas básicas
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    
    # Estadísticas de facturación
    facturas_mes = Factura.objects.filter(
        empresa=empresa,
        fecha_emision__month=hoy.month,
        fecha_emision__year=hoy.year
    )
    
    total_facturado = facturas_mes.aggregate(total=Sum('total'))['total'] or 0
    cantidad_facturas = facturas_mes.count()
    
    # Últimos asientos contables
    ultimos_asientos = Asiento.objects.filter(
        empresa=empresa
    ).order_by('-fecha', '-id')[:5]
    
    # Próximos vencimientos
    proximos_vencimientos = Pago.objects.filter(
        empresa=empresa,
        fecha_vencimiento__gte=hoy,
        estado__in=['pendiente', 'parcial']
    ).order_by('fecha_vencimiento')[:5]
    
    context = {
        'empresa': empresa,
        'titulo': f'Dashboard Contador - {empresa.razon_social}',
        'total_facturado': total_facturado,
        'cantidad_facturas': cantidad_facturas,
        'ultimos_asientos': ultimos_asientos,
        'proximos_vencimientos': proximos_vencimientos,
    }
    
    return render(request, 'empresas/contador/contador_dashboard_empresa.html', context)
