"""
Funciones auxiliares para la generación automática de asientos contables
desde movimientos de tesorería (ingresos y egresos).
"""
from decimal import Decimal
from django.db import transaction
from contabilidad.models import Asiento, Partida, CuentaContable


def generar_numero_asiento(empresa):
    """
    Genera un número consecutivo de asiento para la empresa.
    Formato: ASI-NNNNNN
    """
    ultimo_asiento = Asiento.objects.filter(
        empresa=empresa,
        numero_asiento__startswith='ASI-'
    ).order_by('-numero_asiento').first()
    
    if ultimo_asiento and ultimo_asiento.numero_asiento:
        try:
            ultimo_num = int(ultimo_asiento.numero_asiento.split('-')[1])
            return f'ASI-{str(ultimo_num + 1).zfill(6)}'
        except (ValueError, AttributeError, IndexError):
            return 'ASI-000001'
    return 'ASI-000001'


def obtener_cuenta_banco(empresa, cuenta_bancaria=None):
    """
    Obtiene la cuenta contable de Bancos (1110).
    Si se proporciona una cuenta bancaria específica, intenta obtener su cuenta contable vinculada.
    """
    # Si hay una cuenta bancaria y tiene cuenta contable vinculada, usarla
    if cuenta_bancaria and hasattr(cuenta_bancaria, 'cuenta_contable') and cuenta_bancaria.cuenta_contable:
        return cuenta_bancaria.cuenta_contable
    
    # Caso contrario, buscar la cuenta de bancos genérica (1110)
    try:
        return CuentaContable.objects.get(empresa=empresa, codigo='1110')
    except CuentaContable.DoesNotExist:
        # Si no existe 1110, buscar cualquier cuenta de tipo activo que contenga "banco"
        cuenta = CuentaContable.objects.filter(
            empresa=empresa,
            tipo_cuenta='activo',
            nombre__icontains='banco',
            acepta_movimiento=True
        ).first()
        
        if not cuenta:
            raise ValueError(
                'No se encontró una cuenta contable de Bancos (1110). '
                'Por favor, cree la cuenta en el Plan de Cuentas.'
            )
        return cuenta


def obtener_cuenta_ingresos(empresa):
    """
    Obtiene la cuenta contable de Ingresos por defecto (4105 o similar).
    """
    try:
        # Intentar con 4105 (Ingresos operacionales)
        return CuentaContable.objects.get(empresa=empresa, codigo='4105')
    except CuentaContable.DoesNotExist:
        # Buscar cualquier cuenta de ingresos
        cuenta = CuentaContable.objects.filter(
            empresa=empresa,
            tipo_cuenta='ingreso',
            acepta_movimiento=True
        ).first()
        
        if not cuenta:
            raise ValueError(
                'No se encontró una cuenta de Ingresos (4105). '
                'Por favor, cree la cuenta en el Plan de Cuentas.'
            )
        return cuenta


def obtener_cuenta_gastos(empresa):
    """
    Obtiene la cuenta contable de Gastos por defecto (5105 o similar).
    """
    try:
        # Intentar con 5105 (Gastos administrativos)
        return CuentaContable.objects.get(empresa=empresa, codigo='5105')
    except CuentaContable.DoesNotExist:
        # Buscar cualquier cuenta de gastos
        cuenta = CuentaContable.objects.filter(
            empresa=empresa,
            tipo_cuenta='gasto',
            acepta_movimiento=True
        ).first()
        
        if not cuenta:
            raise ValueError(
                'No se encontró una cuenta de Gastos (5105). '
                'Por favor, cree la cuenta en el Plan de Cuentas.'
            )
        return cuenta


@transaction.atomic
def crear_asiento_ingreso(pago, usuario):
    """
    Crea un asiento contable automático para un ingreso (cobro).
    
    Débito: Banco/Caja (1110) - Aumenta el activo
    Crédito: Ingresos (4105) - Aumenta los ingresos
    
    Args:
        pago: Instancia del modelo Pago con tipo_pago='cobro'
        usuario: Usuario que crea el asiento
    
    Returns:
        Asiento creado
    """
    empresa = pago.empresa
    valor = pago.valor
    
    # Obtener cuentas contables
    cuenta_banco = obtener_cuenta_banco(empresa, pago.cuenta_bancaria)
    cuenta_ingresos = obtener_cuenta_ingresos(empresa)
    
    # Crear asiento
    asiento = Asiento.objects.create(
        empresa=empresa,
        numero_asiento=generar_numero_asiento(empresa),
        fecha_asiento=pago.fecha_pago,
        tipo_asiento='ordinario',
        concepto=f'Ingreso por cobro {pago.numero_pago} - {pago.tercero.razon_social}',
        observaciones=pago.observaciones or '',
        total_debito=valor,
        total_credito=valor,
        estado='confirmado',
        creado_por=usuario,
        confirmado_por=usuario
    )
    
    # Crear partidas
    Partida.objects.create(
        asiento=asiento,
        cuenta=cuenta_banco,
        concepto=f'Ingreso en {cuenta_banco.nombre}',
        valor_debito=valor,
        valor_credito=Decimal('0.00'),
        orden=1,
        tercero=pago.tercero
    )
    
    Partida.objects.create(
        asiento=asiento,
        cuenta=cuenta_ingresos,
        concepto=f'Ingreso por {pago.tercero.razon_social}',
        valor_debito=Decimal('0.00'),
        valor_credito=valor,
        orden=2,
        tercero=pago.tercero
    )
    
    # Vincular asiento al pago
    pago.asiento_contable = asiento
    pago.save(update_fields=['asiento_contable'])
    
    return asiento


@transaction.atomic
def crear_asiento_egreso(pago, usuario):
    """
    Crea un asiento contable automático para un egreso (pago a proveedor).
    
    Débito: Gastos (5105) - Aumenta los gastos
    Crédito: Banco/Caja (1110) - Disminuye el activo
    
    Args:
        pago: Instancia del modelo Pago con tipo_pago='egreso'
        usuario: Usuario que crea el asiento
    
    Returns:
        Asiento creado
    """
    empresa = pago.empresa
    valor = pago.valor
    
    # Obtener cuentas contables
    cuenta_banco = obtener_cuenta_banco(empresa, pago.cuenta_bancaria)
    cuenta_gastos = obtener_cuenta_gastos(empresa)
    
    # Crear asiento
    asiento = Asiento.objects.create(
        empresa=empresa,
        numero_asiento=generar_numero_asiento(empresa),
        fecha_asiento=pago.fecha_pago,
        tipo_asiento='ordinario',
        concepto=f'Egreso por pago {pago.numero_pago} - {pago.tercero.razon_social}',
        observaciones=pago.observaciones or '',
        total_debito=valor,
        total_credito=valor,
        estado='confirmado',
        creado_por=usuario,
        confirmado_por=usuario
    )
    
    # Crear partidas
    Partida.objects.create(
        asiento=asiento,
        cuenta=cuenta_gastos,
        concepto=f'Gasto por {pago.tercero.razon_social}',
        valor_debito=valor,
        valor_credito=Decimal('0.00'),
        orden=1,
        tercero=pago.tercero
    )
    
    Partida.objects.create(
        asiento=asiento,
        cuenta=cuenta_banco,
        concepto=f'Egreso desde {cuenta_banco.nombre}',
        valor_debito=Decimal('0.00'),
        valor_credito=valor,
        orden=2,
        tercero=pago.tercero
    )
    
    # Vincular asiento al pago
    pago.asiento_contable = asiento
    pago.save(update_fields=['asiento_contable'])
    
    return asiento


@transaction.atomic
def anular_asiento_pago(pago):
    """
    Anula el asiento contable asociado a un pago.
    Se usa cuando se elimina un ingreso o egreso.
    
    Args:
        pago: Instancia del modelo Pago
    """
    if pago.asiento_contable:
        asiento = pago.asiento_contable
        asiento.estado = 'anulado'
        asiento.save(update_fields=['estado'])
        return True
    return False
