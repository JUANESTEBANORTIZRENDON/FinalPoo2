from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
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


def es_administrador_holding(user):
    """Verifica si el usuario es administrador del holding"""
    return user.is_superuser or PerfilEmpresa.objects.filter(
        usuario=user, 
        rol='admin',
        activo=True
    ).exists()


@login_required
def dashboard_admin(request):
    """Dashboard principal del administrador del holding"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
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
def gestionar_empresas(request):
    """Vista para gestionar todas las empresas del holding"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
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
def gestionar_usuarios(request):
    """Vista para gestionar todos los usuarios del sistema"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
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
    
    return render(request, 'empresas/admin/gestionar_usuarios.html', context)


@login_required
def asignar_usuario_empresa(request, usuario_id):
    """Vista para asignar un usuario a una empresa con un rol específico"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:login')
    
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        empresa_id = request.POST.get('empresa_id')
        rol = request.POST.get('rol')
        
        if empresa_id and rol:
            empresa = get_object_or_404(Empresa, id=empresa_id)
            
            # Verificar si ya existe la asignación
            perfil_existente = PerfilEmpresa.objects.filter(
                usuario=usuario,
                empresa=empresa
            ).first()
            
            if perfil_existente:
                perfil_existente.rol = rol
                perfil_existente.activo = True
                perfil_existente.asignado_por = request.user
                perfil_existente.save()
                messages.success(request, f'Rol actualizado para {usuario.get_full_name() or usuario.username}')
            else:
                PerfilEmpresa.objects.create(
                    usuario=usuario,
                    empresa=empresa,
                    rol=rol,
                    asignado_por=request.user
                )
                messages.success(request, f'Usuario {usuario.get_full_name() or usuario.username} asignado exitosamente')
            
            return redirect('empresas:admin_gestionar_usuarios')
    
    # Obtener empresas disponibles
    empresas = Empresa.objects.filter(activa=True).order_by('razon_social')
    
    # Obtener asignaciones actuales del usuario
    asignaciones_actuales = PerfilEmpresa.objects.filter(
        usuario=usuario,
        activo=True
    ).select_related('empresa')
    
    context = {
        'usuario': usuario,
        'empresas': empresas,
        'asignaciones_actuales': asignaciones_actuales,
        'roles_choices': PerfilEmpresa.ROL_CHOICES,
    }
    
    return render(request, 'empresas/admin/asignar_usuario.html', context)


@login_required
def desactivar_asignacion(request, perfil_id):
    """Desactivar una asignación de usuario-empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('accounts:login')
    
    perfil = get_object_or_404(PerfilEmpresa, id=perfil_id)
    perfil.activo = False
    perfil.save()
    
    messages.success(request, f'Asignación desactivada para {perfil.usuario.get_full_name() or perfil.usuario.username}')
    return redirect('empresas:admin_gestionar_usuarios')


@login_required
def estadisticas_holding(request):
    """Vista con estadísticas detalladas del holding"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    # Estadísticas por mes (últimos 6 meses)
    fecha_inicio = timezone.now() - timedelta(days=180)
    
    # Empresas creadas por mes
    empresas_por_mes = []
    for i in range(6):
        fecha = timezone.now() - timedelta(days=30*i)
        inicio_mes = fecha.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fin_mes = (inicio_mes + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Empresa.objects.filter(
            fecha_creacion__gte=inicio_mes,
            fecha_creacion__lte=fin_mes
        ).count()
        
        empresas_por_mes.append({
            'mes': inicio_mes.strftime('%B %Y'),
            'count': count
        })
    
    empresas_por_mes.reverse()
    
    # Rendimiento por contador
    contadores = User.objects.filter(
        perfilempresa__rol='contador',
        perfilempresa__activo=True,
        is_active=True
    ).distinct()
    
    rendimiento_contadores = []
    for contador in contadores:
        empresas_asignadas = PerfilEmpresa.objects.filter(
            usuario=contador,
            rol='contador',
            activo=True
        ).count()
        
        facturas_mes = Factura.objects.filter(
            creado_por=contador,
            fecha_creacion__gte=timezone.now() - timedelta(days=30)
        ).count()
        
        rendimiento_contadores.append({
            'contador': contador,
            'empresas_asignadas': empresas_asignadas,
            'facturas_mes': facturas_mes
        })
    
    context = {
        'empresas_por_mes': empresas_por_mes,
        'rendimiento_contadores': rendimiento_contadores,
    }
    
    return render(request, 'empresas/admin/estadisticas.html', context)


@login_required
def ajax_empresa_info(request, empresa_id):
    """Vista AJAX para obtener información de una empresa"""
    if not es_administrador_holding(request.user):
        return JsonResponse({'error': 'Sin permisos'}, status=403)
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # Obtener usuarios asignados
    usuarios = PerfilEmpresa.objects.filter(
        empresa=empresa,
        activo=True
    ).select_related('usuario')
    
    usuarios_data = []
    for perfil in usuarios:
        usuarios_data.append({
            'id': perfil.usuario.id,
            'nombre': perfil.usuario.get_full_name() or perfil.usuario.username,
            'rol': perfil.get_rol_display(),
            'fecha_asignacion': perfil.fecha_asignacion.strftime('%d/%m/%Y')
        })
    
    data = {
        'empresa': {
            'id': empresa.id,
            'razon_social': empresa.razon_social,
            'nit': empresa.nit,
            'email': empresa.email,
            'telefono': empresa.telefono,
            'activa': empresa.activa,
        },
        'usuarios': usuarios_data
    }
    
    return JsonResponse(data)


# ===== VISTAS CRUD PARA EMPRESAS =====

@login_required
def crear_empresa(request):
    """Vista para crear una nueva empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        try:
            # Validar datos requeridos
            razon_social = request.POST.get('razon_social', '').strip()
            nit = request.POST.get('nit', '').strip()
            
            # Validaciones básicas
            if not razon_social:
                messages.error(request, 'La razón social es obligatoria.')
                return render(request, 'empresas/admin/empresa_form.html', {
                    'titulo': 'Crear Nueva Empresa',
                    'accion': 'crear'
                })
            
            if not nit:
                messages.error(request, 'El NIT es obligatorio.')
                return render(request, 'empresas/admin/empresa_form.html', {
                    'titulo': 'Crear Nueva Empresa',
                    'accion': 'crear'
                })
            
            # Validar formato de NIT
            import re
            if not re.match(r'^\d{9,11}-\d{1}$', nit):
                messages.error(request, 'El NIT debe tener el formato correcto: 123456789-0')
                return render(request, 'empresas/admin/empresa_form.html', {
                    'titulo': 'Crear Nueva Empresa',
                    'accion': 'crear'
                })
            
            # Verificar si el NIT ya existe
            if Empresa.objects.filter(nit=nit).exists():
                messages.error(request, f'Ya existe una empresa con el NIT "{nit}".')
                return render(request, 'empresas/admin/empresa_form.html', {
                    'titulo': 'Crear Nueva Empresa',
                    'accion': 'crear'
                })
            
            # Crear empresa
            empresa = Empresa.objects.create(
                razon_social=razon_social,
                nit=nit,
                nombre_comercial=request.POST.get('nombre_comercial', ''),
                email=request.POST.get('email', ''),
                telefono=request.POST.get('telefono', ''),
                direccion=request.POST.get('direccion', ''),
                ciudad=request.POST.get('ciudad', ''),
                departamento=request.POST.get('departamento', ''),
                propietario=request.user,  # Asignar el usuario actual como propietario
                activa=True
            )
            messages.success(request, f'Empresa "{empresa.razon_social}" creada exitosamente.')
            return redirect('empresas:admin_gestionar_empresas')
            
        except Exception as e:
            # Mensajes de error más específicos
            error_msg = str(e)
            if 'UNIQUE constraint failed' in error_msg and 'nit' in error_msg:
                messages.error(request, f'Ya existe una empresa con el NIT "{nit}". Por favor verifica el número.')
            elif 'NOT NULL constraint failed' in error_msg:
                if 'propietario_id' in error_msg:
                    messages.error(request, 'Error interno: No se pudo asignar el propietario. Contacta al administrador.')
                else:
                    messages.error(request, 'Faltan campos obligatorios. Por favor completa toda la información requerida.')
            elif 'CHECK constraint failed' in error_msg:
                messages.error(request, 'Los datos ingresados no cumplen con el formato requerido. Verifica el NIT y otros campos.')
            else:
                messages.error(request, f'Error al crear la empresa: {error_msg}')
            
            return render(request, 'empresas/admin/empresa_form.html', {
                'titulo': 'Crear Nueva Empresa',
                'accion': 'crear'
            })
    
    context = {
        'titulo': 'Crear Nueva Empresa',
        'accion': 'crear'
    }
    return render(request, 'empresas/admin/empresa_form.html', context)


@login_required
def editar_empresa(request, empresa_id):
    """Vista para editar una empresa existente"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        try:
            empresa.razon_social = request.POST.get('razon_social')
            empresa.nit = request.POST.get('nit')
            empresa.nombre_comercial = request.POST.get('nombre_comercial', '')
            empresa.email = request.POST.get('email', '')
            empresa.telefono = request.POST.get('telefono', '')
            empresa.direccion = request.POST.get('direccion', '')
            empresa.ciudad = request.POST.get('ciudad', '')
            empresa.departamento = request.POST.get('departamento', '')
            empresa.activa = request.POST.get('activa') == 'on'
            empresa.save()
            
            messages.success(request, f'Empresa "{empresa.razon_social}" actualizada exitosamente.')
            return redirect('empresas:admin_gestionar_empresas')
        except Exception as e:
            messages.error(request, f'Error al actualizar la empresa: {str(e)}')
    
    context = {
        'titulo': 'Editar Empresa',
        'accion': 'editar',
        'empresa': empresa
    }
    return render(request, 'empresas/admin/empresa_form.html', context)


@login_required
def ver_empresa(request, empresa_id):
    """Vista para ver detalles de una empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    # Obtener usuarios asignados
    usuarios_asignados = PerfilEmpresa.objects.filter(
        empresa=empresa,
        activo=True
    ).select_related('usuario').order_by('rol', 'fecha_asignacion')
    
    # Estadísticas de la empresa
    total_usuarios = usuarios_asignados.count()
    usuarios_por_rol = usuarios_asignados.values('rol').annotate(
        total=Count('id')
    ).order_by('rol')
    
    context = {
        'empresa': empresa,
        'usuarios_asignados': usuarios_asignados,
        'total_usuarios': total_usuarios,
        'usuarios_por_rol': usuarios_por_rol,
    }
    return render(request, 'empresas/admin/empresa_detalle.html', context)


@login_required
def eliminar_empresa(request, empresa_id):
    """Vista para eliminar una empresa"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    empresa = get_object_or_404(Empresa, id=empresa_id)
    
    if request.method == 'POST':
        try:
            razon_social = empresa.razon_social
            # Desactivar en lugar de eliminar para mantener integridad
            empresa.activa = False
            empresa.save()
            
            # Desactivar perfiles asociados
            PerfilEmpresa.objects.filter(empresa=empresa).update(activo=False)
            
            messages.success(request, f'Empresa "{razon_social}" desactivada exitosamente.')
            return redirect('empresas:admin_gestionar_empresas')
        except Exception as e:
            messages.error(request, f'Error al desactivar la empresa: {str(e)}')
    
    # Verificar si tiene datos relacionados
    tiene_usuarios = PerfilEmpresa.objects.filter(empresa=empresa, activo=True).exists()
    
    context = {
        'empresa': empresa,
        'tiene_usuarios': tiene_usuarios,
    }
    return render(request, 'empresas/admin/empresa_eliminar.html', context)


# ===== VISTAS CRUD PARA USUARIOS =====

@login_required
def crear_usuario(request):
    """Vista para crear un nuevo usuario"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        try:
            # Validar datos requeridos
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            password = request.POST.get('password', '').strip()
            password_confirm = request.POST.get('password_confirm', '').strip()
            
            # Validaciones
            if not username:
                messages.error(request, 'El nombre de usuario es obligatorio.')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Crear Nuevo Usuario',
                    'accion': 'crear'
                })
            
            if not email:
                messages.error(request, 'El email es obligatorio.')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Crear Nuevo Usuario',
                    'accion': 'crear'
                })
            
            if not password:
                messages.error(request, 'La contraseña es obligatoria.')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Crear Nuevo Usuario',
                    'accion': 'crear'
                })
            
            if password != password_confirm:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Crear Nuevo Usuario',
                    'accion': 'crear'
                })
            
            # Verificar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Ya existe un usuario con el nombre "{username}".')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Crear Nuevo Usuario',
                    'accion': 'crear'
                })
            
            if User.objects.filter(email=email).exists():
                messages.error(request, f'Ya existe un usuario con el email "{email}".')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Crear Nuevo Usuario',
                    'accion': 'crear'
                })
            
            # Crear usuario
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=True
            )
            
            # Crear perfil de usuario si no existe
            from accounts.models import PerfilUsuario
            if not hasattr(usuario, 'perfilusuario'):
                PerfilUsuario.objects.create(
                    usuario=usuario,
                    documento=request.POST.get('documento', ''),
                    telefono=request.POST.get('telefono', ''),
                    ciudad=request.POST.get('ciudad', ''),
                    direccion=request.POST.get('direccion', '')
                )
            
            messages.success(request, f'Usuario "{usuario.get_full_name() or usuario.username}" creado exitosamente.')
            return redirect('empresas:admin_gestionar_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
    
    context = {
        'titulo': 'Crear Nuevo Usuario',
        'accion': 'crear'
    }
    return render(request, 'empresas/admin/usuario_form.html', context)


@login_required
def editar_usuario(request, usuario_id):
    """Vista para editar un usuario existente"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    usuario = get_object_or_404(User, id=usuario_id)
    
    if request.method == 'POST':
        try:
            # Actualizar datos básicos
            usuario.username = request.POST.get('username', '').strip()
            usuario.email = request.POST.get('email', '').strip()
            usuario.first_name = request.POST.get('first_name', '').strip()
            usuario.last_name = request.POST.get('last_name', '').strip()
            usuario.is_active = request.POST.get('is_active') == 'on'
            
            # Validaciones
            if not usuario.username:
                messages.error(request, 'El nombre de usuario es obligatorio.')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Editar Usuario',
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            if not usuario.email:
                messages.error(request, 'El email es obligatorio.')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Editar Usuario',
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            # Verificar duplicados (excluyendo el usuario actual)
            if User.objects.filter(username=usuario.username).exclude(id=usuario.id).exists():
                messages.error(request, f'Ya existe otro usuario con el nombre "{usuario.username}".')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Editar Usuario',
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            if User.objects.filter(email=usuario.email).exclude(id=usuario.id).exists():
                messages.error(request, f'Ya existe otro usuario con el email "{usuario.email}".')
                return render(request, 'empresas/admin/usuario_form.html', {
                    'titulo': 'Editar Usuario',
                    'accion': 'editar',
                    'usuario': usuario
                })
            
            usuario.save()
            
            # Actualizar perfil si existe
            from accounts.models import PerfilUsuario
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=usuario)
            perfil.documento = request.POST.get('documento', '')
            perfil.telefono = request.POST.get('telefono', '')
            perfil.ciudad = request.POST.get('ciudad', '')
            perfil.direccion = request.POST.get('direccion', '')
            perfil.save()
            
            # Cambiar contraseña si se proporciona
            new_password = request.POST.get('new_password', '').strip()
            if new_password:
                password_confirm = request.POST.get('password_confirm', '').strip()
                if new_password != password_confirm:
                    messages.error(request, 'Las contraseñas no coinciden.')
                    return render(request, 'empresas/admin/usuario_form.html', {
                        'titulo': 'Editar Usuario',
                        'accion': 'editar',
                        'usuario': usuario
                    })
                usuario.set_password(new_password)
                usuario.save()
                messages.info(request, 'Contraseña actualizada exitosamente.')
            
            messages.success(request, f'Usuario "{usuario.get_full_name() or usuario.username}" actualizado exitosamente.')
            return redirect('empresas:admin_gestionar_usuarios')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    
    context = {
        'titulo': 'Editar Usuario',
        'accion': 'editar',
        'usuario': usuario
    }
    return render(request, 'empresas/admin/usuario_form.html', context)


@login_required
def ver_usuario(request, usuario_id):
    """Vista para ver detalles de un usuario"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
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
def historial_cambios(request):
    """Vista para mostrar el historial de cambios de todos los usuarios"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
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
def detalle_historial_cambio(request, cambio_id):
    """Vista para mostrar el detalle completo de un cambio"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    cambio = get_object_or_404(HistorialCambios, id=cambio_id)
    
    context = {
        'cambio': cambio,
    }
    
    return render(request, 'empresas/admin/detalle_historial_cambio.html', context)


@login_required
def exportar_historial(request):
    """Vista para exportar el historial de cambios a CSV/Excel"""
    if not es_administrador_holding(request.user):
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('accounts:login')
    
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Aplicar los mismos filtros que en la vista principal
    usuario_id = request.GET.get('usuario')
    empresa_id = request.GET.get('empresa')
    tipo_accion = request.GET.get('tipo_accion')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    busqueda = request.GET.get('busqueda', '').strip()
    
    historial = HistorialCambios.objects.select_related('usuario', 'empresa').exclude(
        usuario__is_superuser=True  # Excluir administradores del holding
    )
    
    # Aplicar filtros (mismo código que en historial_cambios)
    if usuario_id:
        historial = historial.filter(usuario_id=usuario_id)
    if empresa_id:
        historial = historial.filter(empresa_id=empresa_id)
    if tipo_accion:
        historial = historial.filter(tipo_accion=tipo_accion)
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
    if busqueda:
        from django.db.models import Q
        historial = historial.filter(
            Q(descripcion__icontains=busqueda) |
            Q(usuario__username__icontains=busqueda) |
            Q(empresa__razon_social__icontains=busqueda)
        )
    
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
        writer.writerow([
            cambio.fecha_hora.strftime('%d/%m/%Y %H:%M:%S'),
            cambio.usuario.get_full_name() or cambio.usuario.username,
            cambio.empresa.razon_social if cambio.empresa else 'N/A',
            cambio.get_tipo_accion_display(),
            cambio.descripcion,
            cambio.rol_usuario,
            cambio.ip_address or 'N/A',
            'Sí' if cambio.exitosa else 'No',
            cambio.mensaje_error or 'N/A'
        ])
    
    return response
