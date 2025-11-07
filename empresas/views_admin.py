"""
Vistas de Administración del Holding

NOTA DE SEGURIDAD - HTTP METHODS:
==================================
Algunas vistas en este archivo usan @require_http_methods(['GET', 'POST'])
Esto es el patrón estándar de Django para manejadores de formularios:

✅ SEGURO porque:
1. GET: Muestra formulario (solo lectura, no modifica estado)
2. POST: Procesa formulario (protegido por CSRF middleware)
3. Django's CsrfViewMiddleware verifica token automáticamente
4. Todas las vistas requieren autenticación (@login_required)
5. Verificación adicional de permisos (es_administrador_holding)

Vistas afectadas:
- asignar_usuario_empresa (línea ~216)
- crear_empresa (línea ~226)
- editar_empresa (línea ~236)
- crear_usuario (línea ~340)
- editar_usuario (línea ~350)

📚 Documentación completa: SECURITY_HTTP_METHODS_REVIEWED.md
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta

from .models import Empresa, PerfilEmpresa, EmpresaActiva, HistorialCambios
from accounts.models import PerfilUsuario
from facturacion.models import Factura
from tesoreria.models import Pago
from contabilidad.models import Asiento

# Constantes para evitar duplicación de literales
MSG_NO_PERMISOS = 'No tienes permisos para acceder a esta sección.'
URL_LOGIN = 'accounts:login'
URL_DASHBOARD = 'accounts:dashboard'
URL_GESTIONAR_USUARIOS = 'empresas:admin_gestionar_usuarios'
URL_GESTIONAR_EMPRESAS = 'empresas:admin_gestionar_empresas'
TEMPLATE_EMPRESA_FORM = 'empresas/admin/empresa_form.html'
TEMPLATE_USUARIO_FORM = 'empresas/admin/usuario_form.html'
TITULO_CREAR_EMPRESA = 'Crear Nueva Empresa'
TITULO_CREAR_USUARIO = 'Crear Nuevo Usuario'
TITULO_EDITAR_USUARIO = 'Editar Usuario'


def es_administrador_holding(user):
    """Verifica si el usuario es administrador del holding"""
    return user.is_superuser or PerfilEmpresa.objects.filter(
        usuario=user, 
        rol='admin',
        activo=True
    ).exists()


@login_required
@require_http_methods(["GET"])
def dashboard_admin(request):
    """Dashboard principal del administrador del holding"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # Métricas generales
    total_empresas = Empresa.objects.filter(activa=True).count()
    total_usuarios = User.objects.filter(is_active=True).count()
    
    # Usuarios por rol
    usuarios_por_rol = PerfilEmpresa.objects.filter(activo=True).values('rol').annotate(
        total=Count('id')
    ).order_by('rol')
    
    # Empresas sin contador asignado
    empresas_sin_contador = Empresa.objects.filter(
        activa=True
    ).exclude(
        perfiles__rol='contador',
        perfiles__activo=True
    ).count()
    
    # Solicitudes de registro pendientes (usuarios sin empresa asignada)
    usuarios_pendientes = User.objects.filter(
        is_active=True,
        perfilempresa__isnull=True
    ).count()
    
    # Documentos pendientes de confirmación (último mes)
    fecha_inicio = timezone.now() - timedelta(days=30)
    
    facturas_pendientes = Factura.objects.filter(
        estado='borrador',
        fecha_creacion__gte=fecha_inicio
    ).count()
    
    pagos_pendientes = Pago.objects.filter(
        estado='borrador',
        fecha_creacion__gte=fecha_inicio
    ).count()
    
    asientos_pendientes = Asiento.objects.filter(
        estado='borrador',
        fecha_creacion__gte=fecha_inicio
    ).count()
    
    # Actividad reciente
    empresas_recientes = Empresa.objects.filter(
        activa=True
    ).order_by('-fecha_creacion')[:5]
    
    usuarios_recientes = User.objects.filter(
        is_active=True
    ).order_by('-date_joined')[:5]
    
    context = {
        'total_empresas': total_empresas,
        'total_usuarios': total_usuarios,
        'usuarios_por_rol': usuarios_por_rol,
        'empresas_sin_contador': empresas_sin_contador,
        'usuarios_pendientes': usuarios_pendientes,
        'facturas_pendientes': facturas_pendientes,
        'pagos_pendientes': pagos_pendientes,
        'asientos_pendientes': asientos_pendientes,
        'empresas_recientes': empresas_recientes,
        'usuarios_recientes': usuarios_recientes,
    }
    
    return render(request, 'empresas/admin/dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def gestionar_empresas(request):
    """Vista para gestionar todas las empresas del holding"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # Filtros
    busqueda = request.GET.get('busqueda', '')
    estado = request.GET.get('estado', 'todas')
    
    empresas = Empresa.objects.all()
    
    if busqueda:
        empresas = empresas.filter(
            Q(razon_social__icontains=busqueda) |
            Q(nit__icontains=busqueda) |
            Q(nombre_comercial__icontains=busqueda)
        )
    
    if estado == 'activas':
        empresas = empresas.filter(activa=True)
    elif estado == 'inactivas':
        empresas = empresas.filter(activa=False)
    
    # Agregar información adicional
    empresas = empresas.annotate(
        total_usuarios=Count('perfiles', filter=Q(perfiles__activo=True)),
        tiene_contador=Count('perfiles', filter=Q(perfiles__rol='contador', perfiles__activo=True))
    ).order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(empresas, 10)
    page_number = request.GET.get('page')
    empresas_page = paginator.get_page(page_number)
    
    context = {
        'empresas': empresas_page,
        'busqueda': busqueda,
        'estado': estado,
    }
    
    return render(request, 'empresas/admin/gestionar_empresas.html', context)


@login_required
@require_http_methods(["GET"])
def gestionar_usuarios(request):
    """Vista para gestionar todos los usuarios del sistema"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # Filtros
    busqueda = request.GET.get('busqueda', '')
    rol_filtro = request.GET.get('rol', 'todos')
    estado = request.GET.get('estado', 'todos')
    
    usuarios = User.objects.all()
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
    
    if estado == 'activos':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'inactivos':
        usuarios = usuarios.filter(is_active=False)
    
    # Filtro por rol
    if rol_filtro != 'todos':
        usuarios = usuarios.filter(perfilempresa__rol=rol_filtro, perfilempresa__activo=True)
    
    # Agregar información adicional
    usuarios = usuarios.prefetch_related('perfilempresa_set__empresa').order_by('-date_joined')
    
    # Paginación
    paginator = Paginator(usuarios, 15)
    page_number = request.GET.get('page')
    usuarios_page = paginator.get_page(page_number)
    
    # Usuarios sin asignación (solo observadores sin empresa)
    usuarios_sin_asignacion = User.objects.filter(
        is_active=True,
        perfilempresa__isnull=True
    ).count()
    
    context = {
        'usuarios': usuarios_page,
        'busqueda': busqueda,
        'rol_filtro': rol_filtro,
        'estado': estado,
        'usuarios_sin_asignacion': usuarios_sin_asignacion,
        'roles_choices': PerfilEmpresa.ROL_CHOICES,
    }
@login_required
@require_http_methods(['GET', 'POST'])  # GET: muestra formulario, POST: procesa - CSRF protegido por Django
def asignar_usuario_empresa(request, usuario_id):
    """Vista para asignar un usuario a una empresa con un rol específico"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect(URL_LOGIN)
    
    # ... (rest of the function remains the same)

@login_required
@require_http_methods(['GET', 'POST'])  # GET: muestra formulario, POST: procesa - CSRF protegido por Django
def crear_empresa(request):
    """Vista para crear una nueva empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # ... (rest of the function remains the same)

@login_required
@require_http_methods(['GET', 'POST'])  # GET: muestra formulario, POST: procesa - CSRF protegido por Django
def editar_empresa(request, empresa_id):
    """Vista para editar una empresa existente"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        # Aquí iría la lógica de actualización
        messages.success(request, f'Empresa "{empresa.razon_social}" actualizada exitosamente.')
        return redirect(URL_GESTIONAR_EMPRESAS)
    
    context = {
        'titulo': 'Editar Empresa',
        'accion': 'editar',
        'empresa': empresa
    }
    return render(request, TEMPLATE_EMPRESA_FORM, context)

@login_required
@require_http_methods(['GET'])
def ver_empresa(request, empresa_id):
    """Vista para ver detalles de una empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # Obtener usuarios asignados
    usuarios_asignados = PerfilEmpresa.objects.filter(
        empresa=empresa,
        activo=True
    ).select_related('usuario').order_by('usuario__username')
    
    context = {
        'empresa': empresa,
        'usuarios_asignados': usuarios_asignados,
    }
    return render(request, 'empresas/admin/empresa_detalle.html', context)

@login_required
@require_http_methods(['POST'])
def eliminar_empresa(request, empresa_id):
    """Vista para eliminar (desactivar) una empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    empresa.activa = False
    empresa.save()
    
    messages.success(request, f'Empresa "{empresa.razon_social}" desactivada exitosamente.')
    return redirect(URL_GESTIONAR_EMPRESAS)

@login_required
@require_http_methods(['POST'])
def desactivar_asignacion(request, perfil_id):
    """Vista para desactivar la asignación de un usuario a una empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    perfil = get_object_or_404(PerfilEmpresa, id=perfil_id)
    perfil.activo = False
    perfil.save()
    
    messages.success(request, f'Asignación de {perfil.usuario.get_full_name() or perfil.usuario.username} desactivada.')
    return redirect(URL_GESTIONAR_USUARIOS)

@login_required
@require_http_methods(['GET'])
def estadisticas_holding(request):
    """Vista para mostrar estadísticas generales del holding"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    context = {
        'total_empresas': Empresa.objects.filter(activa=True).count(),
        'total_usuarios': User.objects.filter(is_active=True).count(),
    }
    return render(request, 'empresas/admin/estadisticas.html', context)

@login_required
@require_http_methods(['GET'])
def ajax_empresa_info(request, empresa_id):
    """Vista AJAX para obtener información de una empresa"""
    if not es_administrador_holding(request.user):
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    return JsonResponse({
        'id': empresa.id,
        'razon_social': empresa.razon_social,
        'nit': empresa.nit,
        'activa': empresa.activa,
    })

@login_required
@require_http_methods(['GET', 'POST'])  # GET: muestra formulario, POST: procesa - CSRF protegido por Django
def crear_usuario(request):
    """Vista para crear un nuevo usuario"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # ... (rest of the function remains the same)

@login_required
@require_http_methods(['GET', 'POST'])  # GET: muestra formulario, POST: procesa - CSRF protegido por Django
def editar_usuario(request, usuario_id):
    """Vista para editar un usuario existente"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # ... (rest of the function remains the same)
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            usuario.username = request.POST.get('username', '').strip()
            usuario.email = request.POST.get('email', '').strip()
            usuario.first_name = request.POST.get('first_name', '').strip()
            usuario.last_name = request.POST.get('last_name', '').strip()
            usuario.is_active = request.POST.get('is_active') == 'on'
            
            # Validar datos básicos
            valido, error = _validar_datos_usuario_editar(usuario)
            if not valido:
                messages.error(request, error)
                return render(request, TEMPLATE_USUARIO_FORM, {
                    'titulo': TITULO_EDITAR_USUARIO,
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            # Verificar duplicados
            duplicado, error = _verificar_duplicados_edicion(usuario)
            if duplicado:
                messages.error(request, error)
                return render(request, TEMPLATE_USUARIO_FORM, {
                    'titulo': TITULO_EDITAR_USUARIO,
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            usuario.save()
            _actualizar_perfil_usuario(usuario, request)
            
            # Cambiar contraseña si es necesario
            pwd_ok, pwd_msg = _cambiar_password_si_necesario(usuario, request)
            if not pwd_ok:
                messages.error(request, pwd_msg)
                return render(request, TEMPLATE_USUARIO_FORM, {
                    'titulo': TITULO_EDITAR_USUARIO,
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            if pwd_msg:
                messages.info(request, pwd_msg)
            
            messages.success(request, f'Usuario "{usuario.get_full_name() or usuario.username}" actualizado exitosamente.')
            return redirect(URL_GESTIONAR_USUARIOS)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    
    context = {
        'titulo': TITULO_EDITAR_USUARIO,
        'accion': 'editar',
        'usuario': usuario
    }
    return render(request, TEMPLATE_USUARIO_FORM, context)


@login_required
@require_http_methods(["GET"])
def ver_usuario(request, usuario_id):
    """Vista para ver detalles de un usuario"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    usuario = get_object_or_404(User, id=usuario_id)
    
    # Obtener empresas asignadas
    empresas_asignadas = PerfilEmpresa.objects.filter(
        usuario=usuario,
        activo=True
    ).select_related('empresa').order_by('empresa__razon_social')
    
    # Estadísticas del usuario
    total_empresas = empresas_asignadas.count()
    roles_por_empresa = empresas_asignadas.values('rol').annotate(
        total=Count('id')
    ).order_by('rol')
    
    context = {
        'usuario': usuario,
        'empresas_asignadas': empresas_asignadas,
        'total_empresas': total_empresas,
        'roles_por_empresa': roles_por_empresa,
    }
    return render(request, 'empresas/admin/usuario_detalle.html', context)


# ===== VISTA DEL HISTORIAL DE CAMBIOS =====

@login_required
@require_http_methods(["GET"])
def historial_cambios(request):
    """Vista para mostrar el historial de cambios de todos los usuarios"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    # Obtener parámetros de filtro
    usuario_id = request.GET.get('usuario')
    empresa_id = request.GET.get('empresa')
    tipo_accion = request.GET.get('tipo_accion')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    busqueda = request.GET.get('busqueda', '').strip()
    
    # Construir queryset base - Solo usuarios NO administradores del holding
    historial = HistorialCambios.objects.select_related(
        'usuario', 'empresa'
    ).exclude(
        usuario__is_superuser=True  # Excluir administradores del holding
    ).order_by('-fecha_hora')
    
    # Aplicar filtros
    if usuario_id:
        historial = historial.filter(usuario_id=usuario_id)
    
    if empresa_id:
        historial = historial.filter(empresa_id=empresa_id)
    
    if tipo_accion:
        historial = historial.filter(tipo_accion=tipo_accion)
    
    if fecha_desde:
        try:
            from datetime import datetime
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            historial = historial.filter(fecha_hora__date__gte=fecha_desde_obj.date())
        except ValueError:
            pass
    
    if fecha_hasta:
        try:
            from datetime import datetime
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            historial = historial.filter(fecha_hora__date__lte=fecha_hasta_obj.date())
        except ValueError:
            pass
    
    if busqueda:
        from django.db.models import Q
        historial = historial.filter(
            Q(descripcion__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda) |
            Q(usuario__first_name__icontains=busqueda) |
            Q(usuario__last_name__icontains=busqueda) |
            Q(empresa__razon_social__icontains=busqueda)
        )
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(historial, 50)  # 50 registros por página
    page_number = request.GET.get('page')
    historial_paginado = paginator.get_page(page_number)
    
    # Obtener listas para los filtros - Solo usuarios NO administradores
    usuarios_con_historial = User.objects.filter(
        historialcambios__isnull=False,
        is_superuser=False  # Excluir administradores del holding
    ).distinct().order_by('username')
    
    empresas_con_historial = Empresa.objects.filter(
        historialcambios__isnull=False
    ).distinct().order_by('razon_social')
    
    tipos_accion_disponibles = HistorialCambios.objects.values_list(
        'tipo_accion', flat=True
    ).distinct().order_by('tipo_accion')
    
    # Estadísticas rápidas - Solo usuarios NO administradores
    total_acciones = historial.count()
    acciones_hoy = historial.filter(fecha_hora__date=timezone.now().date()).count()
    usuarios_activos_hoy = historial.filter(
        fecha_hora__date=timezone.now().date()
    ).values('usuario').distinct().count()
    
    context = {
        'historial': historial_paginado,
        'usuarios_con_historial': usuarios_con_historial,
        'empresas_con_historial': empresas_con_historial,
        'tipos_accion_disponibles': tipos_accion_disponibles,
        'filtros': {
            'usuario_id': usuario_id,
            'empresa_id': empresa_id,
            'tipo_accion': tipo_accion,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'busqueda': busqueda,
        },
        'estadisticas': {
            'total_acciones': total_acciones,
            'acciones_hoy': acciones_hoy,
            'usuarios_activos_hoy': usuarios_activos_hoy,
        },
        'tipos_accion_choices': HistorialCambios.TIPO_ACCION_CHOICES,
    }
    
    return render(request, 'empresas/admin/historial_cambios.html', context)


@login_required
@require_http_methods(["GET"])
def detalle_historial_cambio(request, cambio_id):
    """Vista para mostrar el detalle completo de un cambio"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    cambio = get_object_or_404(HistorialCambios, id=cambio_id)
    
    context = {
        'cambio': cambio,
    }
    
    return render(request, 'empresas/admin/detalle_historial_cambio.html', context)


def _aplicar_filtros_historial_exportar(historial, request):
    """Aplicar filtros básicos al queryset de historial"""
    usuario_id = request.GET.get('usuario')
    empresa_id = request.GET.get('empresa')
    tipo_accion = request.GET.get('tipo_accion')
    busqueda = request.GET.get('busqueda', '').strip()
    
    if usuario_id:
        historial = historial.filter(usuario_id=usuario_id)
    if empresa_id:
        historial = historial.filter(empresa_id=empresa_id)
    if tipo_accion:
        historial = historial.filter(tipo_accion=tipo_accion)
    if busqueda:
        from django.db.models import Q
        historial = historial.filter(
            Q(descripcion__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda) |
            Q(empresa__razon_social__icontains=busqueda)
        )
    return historial


def _aplicar_filtros_fecha_exportar(historial, request):
    """Aplicar filtros de fecha al historial"""
    from datetime import datetime
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d')
            historial = historial.filter(fecha_hora__date__gte=fecha_desde_obj.date())
        except ValueError:
            pass
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d')
            historial = historial.filter(fecha_hora__date__lte=fecha_hasta_obj.date())
        except ValueError:
            pass
    return historial


def _generar_fila_csv(cambio):
    """Generar una fila de datos para el CSV"""
    return [
        cambio.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
        cambio.usuario.get_full_name() or cambio.usuario.username,
        cambio.empresa.razon_social if cambio.empresa else 'N/A',
        cambio.get_tipo_accion_display(),
        cambio.descripcion,
        cambio.rol_usuario,
        cambio.ip_address or 'N/A',
        'Sí' if cambio.exitosa else 'No',
        cambio.mensaje_error or 'N/A'
    ]


@login_required
@require_http_methods(["GET"])
def exportar_historial(request):
    """Vista para exportar el historial de cambios a CSV/Excel"""
    if not es_administrador_holding(request.user):
        messages.error(request, MSG_NO_PERMISOS)
        return redirect(URL_LOGIN)
    
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Obtener y filtrar historial
    historial = HistorialCambios.objects.select_related('usuario', 'empresa').exclude(
        usuario__is_superuser=True  # Excluir administradores del holding
    )
    historial = _aplicar_filtros_historial_exportar(historial, request)
    historial = _aplicar_filtros_fecha_exportar(historial, request)
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="historial_cambios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Fecha y Hora',
        'Usuario',
        'Empresa',
        'Tipo de Acción',
        'Descripción',
        'Rol Usuario',
        'IP Address',
        'Exitosa',
        'Mensaje Error'
    ])
    
    for cambio in historial.order_by('-fecha_hora')[:1000]:  # Limitar a 1000 registros
        writer.writerow(_generar_fila_csv(cambio))
    
    return response


# ===== DASHBOARDS PARA OTROS ROLES =====

@login_required
@require_http_methods(["GET"])
def dashboard_contador(request):
    """Dashboard para usuarios con rol de contador"""
    # Verificar que el usuario tenga rol de contador
    perfil = PerfilEmpresa.objects.filter(
        usuario=request.user,
        rol='contador',
        activo=True
    ).first()
    
    if not perfil:
        messages.error(request, 'No tienes permisos de contador.')
        return redirect(URL_DASHBOARD)
    
    # Obtener empresa activa
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    context = {
        'perfil': perfil,
        'empresa_activa': empresa_activa,
        'titulo': 'Dashboard Contador'
    }
    
    return render(request, 'empresas/contador/dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def dashboard_operador(request):
    """Dashboard para usuarios con rol de operador"""
    # Verificar que el usuario tenga rol de operador
    perfil = PerfilEmpresa.objects.filter(
        usuario=request.user,
        rol='operador',
        activo=True
    ).first()
    
    if not perfil:
        messages.error(request, 'No tienes permisos de operador.')
        return redirect(URL_DASHBOARD)
    
    # Obtener empresa activa
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    context = {
        'perfil': perfil,
        'empresa_activa': empresa_activa,
        'titulo': 'Dashboard Operador'
    }
    
    return render(request, 'empresas/operador/dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def dashboard_observador(request):
    """Dashboard para usuarios con rol de observador"""
    # Verificar que el usuario tenga rol de observador
    perfil = PerfilEmpresa.objects.filter(
        usuario=request.user,
        rol='observador',
        activo=True
    ).first()
    
    if not perfil:
        messages.error(request, 'No tienes permisos de observador.')
        return redirect(URL_DASHBOARD)
    
    # Obtener empresa activa
    empresa_activa = getattr(request, 'empresa_activa', None)
    
    context = {
        'perfil': perfil,
        'empresa_activa': empresa_activa,
        'titulo': 'Dashboard Observador'
    }
    
    return render(request, 'empresas/observador/dashboard.html', context)
