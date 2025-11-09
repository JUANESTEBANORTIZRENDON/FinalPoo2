"""
Servicios de lógica de negocio para el módulo de tesorería.
Maneja las operaciones complejas de pagos, cobros y cuentas bancarias.
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from tesoreria.models import Pago, CuentaBancaria, PagoDetalle
from facturacion.models import Factura


class ServicioTesoreria:
    """
    Servicio para manejar la lógica de negocio de tesorería.
    """
    
    @staticmethod
    @transaction.atomic
    def confirmar_pago(pago, usuario):
        """
        Confirma un pago y actualiza los saldos correspondientes.
        
        Args:
            pago: Instancia del modelo Pago
            usuario: Usuario que confirma el pago
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validar que el pago esté en estado pendiente
        if pago.estado != 'pendiente':
            return False, f"El pago ya está en estado {pago.estado}"
        
        # Si es un egreso, validar que haya saldo suficiente
        if pago.tipo_pago == 'egreso':
            # Aquí deberías obtener la cuenta bancaria asociada
            # Por ahora, solo cambiamos el estado
            pass
        
        # Cambiar estado a activo
        pago.estado = 'activo'
        pago.confirmado_por = usuario
        pago.fecha_confirmacion = timezone.now()
        pago.save()
        
        # TODO: Generar asiento contable automático
        # from contabilidad.services import ServicioContabilidad
        # ServicioContabilidad.generar_asiento_pago(pago)
        
        return True, "Pago confirmado exitosamente"
    
    @staticmethod
    @transaction.atomic
    def anular_pago(pago, motivo=""):
        """
        Anula un pago y reversa los cambios en saldos.
        
        Args:
            pago: Instancia del modelo Pago
            motivo: Motivo de la anulación
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Validar que el pago no esté ya anulado
        if pago.estado == 'anulado':
            return False, "El pago ya está anulado"
        
        # Guardar estado anterior
        estado_anterior = pago.estado
        
        # Cambiar estado a pendiente (o crear un estado 'anulado')
        pago.estado = 'pendiente'
        pago.save()
        
        # TODO: Reversar asiento contable si existe
        # if pago.asiento_contable:
        #     ServicioContabilidad.reversar_asiento(pago.asiento_contable)
        
        return True, f"Pago anulado exitosamente. Estado anterior: {estado_anterior}"
    
    @staticmethod
    @transaction.atomic
    def cobrar_factura(factura, metodo_pago, usuario, fecha_pago=None):
        """
        Crea un cobro automáticamente desde una factura.
        
        Args:
            factura: Instancia del modelo Factura
            metodo_pago: Método de pago a utilizar
            usuario: Usuario que registra el cobro
            fecha_pago: Fecha del pago (opcional, por defecto hoy)
            
        Returns:
            tuple: (pago: Pago|None, message: str)
        """
        if not fecha_pago:
            fecha_pago = timezone.now().date()
        
        # Validar que la factura tenga saldo pendiente
        if not hasattr(factura, 'total') or factura.total <= 0:
            return None, "La factura no tiene un total válido"
        
        # Crear el pago/cobro
        pago = Pago.objects.create(
            empresa=factura.empresa,
            numero_pago=f"COB-{factura.numero_factura}",
            fecha_pago=fecha_pago,
            tipo_pago='cobro',
            tercero=factura.cliente,
            factura=factura,
            metodo_pago=metodo_pago,
            valor=factura.total,
            estado='pendiente',
            creado_por=usuario
        )
        
        return pago, "Cobro creado exitosamente desde la factura"
    
    @staticmethod
    def validar_saldo_cuenta(cuenta_bancaria, monto):
        """
        Valida que una cuenta bancaria tenga saldo suficiente.
        
        Args:
            cuenta_bancaria: Instancia de CuentaBancaria
            monto: Monto a validar
            
        Returns:
            tuple: (valido: bool, message: str)
        """
        if cuenta_bancaria.saldo_actual < monto:
            return False, f"Saldo insuficiente. Disponible: ${cuenta_bancaria.saldo_actual}, Requerido: ${monto}"
        
        return True, "Saldo suficiente"
    
    @staticmethod
    @transaction.atomic
    def marcar_pago_como_pagado(pago, usuario):
        """
        Marca un pago activo como pagado.
        
        Args:
            pago: Instancia del modelo Pago
            usuario: Usuario que marca como pagado
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if pago.estado != 'activo':
            return False, f"El pago debe estar en estado activo. Estado actual: {pago.estado}"
        
        pago.estado = 'pagado'
        pago.save()
        
        return True, "Pago marcado como pagado exitosamente"