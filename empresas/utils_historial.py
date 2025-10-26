"""
Utilidades para registrar acciones en el historial de cambios
"""
from .models import HistorialCambios, EmpresaActiva


def registrar_login(usuario, request):
    """Registra el inicio de sesión de un usuario"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='usuario_login',
        descripcion=f'Usuario {usuario.get_full_name() or usuario.username} inició sesión',
        empresa=empresa,
        request=request
    )


def registrar_logout(usuario, request):
    """Registra el cierre de sesión de un usuario"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='usuario_logout',
        descripcion=f'Usuario {usuario.get_full_name() or usuario.username} cerró sesión',
        empresa=empresa,
        request=request
    )


def registrar_cambio_empresa(usuario, empresa_anterior, empresa_nueva, request):
    """Registra el cambio de empresa activa"""
    descripcion = 'Cambió de empresa activa'
    if empresa_anterior:
        descripcion += f' desde "{empresa_anterior.razon_social}"'
    if empresa_nueva:
        descripcion += f' hacia "{empresa_nueva.razon_social}"'
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='usuario_cambio_empresa',
        descripcion=descripcion,
        empresa=empresa_nueva,
        request=request
    )


def registrar_creacion_empresa(usuario, empresa, request):
    """Registra la creación de una empresa"""
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='empresa_crear',
        descripcion=f'Empresa "{empresa.razon_social}" creada (NIT: {empresa.nit})',
        empresa=empresa,
        modelo_afectado='Empresa',
        objeto_id=empresa.id,
        request=request
    )


def registrar_edicion_empresa(usuario, empresa, datos_anteriores, datos_nuevos, request):
    """Registra la edición de una empresa"""
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='empresa_editar',
        descripcion=f'Empresa "{empresa.razon_social}" editada',
        empresa=empresa,
        modelo_afectado='Empresa',
        objeto_id=empresa.id,
        datos_anteriores=datos_anteriores,
        datos_nuevos=datos_nuevos,
        request=request
    )


def registrar_activacion_empresa(usuario, empresa, request):
    """Registra la activación de una empresa"""
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='empresa_activar',
        descripcion=f'Empresa "{empresa.razon_social}" activada',
        empresa=empresa,
        modelo_afectado='Empresa',
        objeto_id=empresa.id,
        request=request
    )


def registrar_desactivacion_empresa(usuario, empresa, request):
    """Registra la desactivación de una empresa"""
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='empresa_desactivar',
        descripcion=f'Empresa "{empresa.razon_social}" desactivada',
        empresa=empresa,
        modelo_afectado='Empresa',
        objeto_id=empresa.id,
        request=request
    )


def registrar_creacion_tercero(usuario, tercero, request):
    """Registra la creación de un tercero"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='tercero_crear',
        descripcion=f'Tercero "{tercero.razon_social}" creado (Doc: {tercero.numero_documento})',
        empresa=empresa,
        modelo_afectado='Tercero',
        objeto_id=tercero.id,
        request=request
    )


def registrar_edicion_tercero(usuario, tercero, request):
    """Registra la edición de un tercero"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='tercero_editar',
        descripcion=f'Tercero "{tercero.razon_social}" editado',
        empresa=empresa,
        modelo_afectado='Tercero',
        objeto_id=tercero.id,
        request=request
    )


def registrar_eliminacion_tercero(usuario, tercero, request):
    """Registra la eliminación de un tercero"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='tercero_eliminar',
        descripcion=f'Tercero "{tercero.razon_social}" eliminado',
        empresa=empresa,
        modelo_afectado='Tercero',
        objeto_id=tercero.id,
        request=request
    )


def registrar_creacion_factura(usuario, factura, request):
    """Registra la creación de una factura"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='factura_crear',
        descripcion=f'Factura #{factura.numero} creada por valor ${factura.total:,.2f}',
        empresa=empresa,
        modelo_afectado='Factura',
        objeto_id=factura.id,
        request=request
    )


def registrar_edicion_factura(usuario, factura, request):
    """Registra la edición de una factura"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='factura_editar',
        descripcion=f'Factura #{factura.numero} editada',
        empresa=empresa,
        modelo_afectado='Factura',
        objeto_id=factura.id,
        request=request
    )


def registrar_anulacion_factura(usuario, factura, request):
    """Registra la anulación de una factura"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='factura_anular',
        descripcion=f'Factura #{factura.numero} anulada',
        empresa=empresa,
        modelo_afectado='Factura',
        objeto_id=factura.id,
        request=request
    )


def registrar_pago_factura(usuario, factura, monto_pago, request):
    """Registra el pago de una factura"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='factura_pagar',
        descripcion=f'Pago de ${monto_pago:,.2f} aplicado a factura #{factura.numero}',
        empresa=empresa,
        modelo_afectado='Factura',
        objeto_id=factura.id,
        request=request
    )


def registrar_creacion_pago(usuario, pago, request):
    """Registra la creación de un pago"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='pago_crear',
        descripcion=f'Pago registrado por ${pago.valor:,.2f}',
        empresa=empresa,
        modelo_afectado='Pago',
        objeto_id=pago.id,
        request=request
    )


def registrar_creacion_asiento(usuario, asiento, request):
    """Registra la creación de un asiento contable"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='asiento_crear',
        descripcion=f'Asiento contable #{asiento.numero} creado',
        empresa=empresa,
        modelo_afectado='Asiento',
        objeto_id=asiento.id,
        request=request
    )


def registrar_generacion_reporte(usuario, tipo_reporte, parametros, request):
    """Registra la generación de un reporte"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    descripcion = f'Reporte "{tipo_reporte}" generado'
    if parametros:
        descripcion += f' con parámetros: {parametros}'
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='reporte_generar',
        descripcion=descripcion,
        empresa=empresa,
        request=request
    )


def registrar_exportacion_reporte(usuario, tipo_reporte, formato, request):
    """Registra la exportación de un reporte"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='reporte_exportar',
        descripcion=f'Reporte "{tipo_reporte}" exportado en formato {formato}',
        empresa=empresa,
        request=request
    )


def registrar_acceso_denegado(usuario, recurso, request):
    """Registra un intento de acceso denegado"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='acceso_denegado',
        descripcion=f'Acceso denegado a: {recurso}',
        empresa=empresa,
        request=request,
        exitosa=False,
        mensaje_error='Permisos insuficientes'
    )


def registrar_error_sistema(usuario, error_mensaje, request):
    """Registra un error del sistema"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa if usuario else None
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='error_sistema',
        descripcion=f'Error del sistema: {error_mensaje}',
        empresa=empresa,
        request=request,
        exitosa=False,
        mensaje_error=error_mensaje
    )


def registrar_actualizacion_perfil(usuario, request):
    """Registra la actualización del perfil de usuario"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='usuario_perfil_actualizado',
        descripcion='Perfil de usuario actualizado',
        empresa=empresa,
        request=request
    )


def registrar_cambio_configuracion(usuario, configuracion, valor_anterior, valor_nuevo, request):
    """Registra un cambio en la configuración del sistema"""
    try:
        empresa = EmpresaActiva.objects.get(usuario=usuario).empresa
    except EmpresaActiva.DoesNotExist:
        empresa = None
    
    HistorialCambios.registrar_accion(
        usuario=usuario,
        tipo_accion='configuracion_cambiar',
        descripcion=f'Configuración "{configuracion}" cambiada de "{valor_anterior}" a "{valor_nuevo}"',
        empresa=empresa,
        datos_anteriores={'configuracion': configuracion, 'valor': valor_anterior},
        datos_nuevos={'configuracion': configuracion, 'valor': valor_nuevo},
        request=request
    )
