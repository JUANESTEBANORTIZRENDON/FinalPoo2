"""
Servicios de dominio para la contabilidad.
Contiene la lógica de negocio para generar asientos contables automáticos.
"""

from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import Asiento, Partida, CuentaContable


class ServicioContabilidad:
    """
    Servicio principal para operaciones contables.
    Maneja la generación automática de asientos contables.
    """
    
    @staticmethod
    def obtener_siguiente_numero_asiento(empresa):
        """
        Obtiene el siguiente número de asiento para una empresa.
        
        Args:
            empresa: Instancia de Empresa
            
        Returns:
            str: Siguiente número de asiento
        """
        ultimo_asiento = Asiento.objects.filter(empresa=empresa).order_by('-numero_asiento').first()
        
        if ultimo_asiento:
            try:
                ultimo_numero = int(ultimo_asiento.numero_asiento)
                return str(ultimo_numero + 1).zfill(6)  # Formato: 000001
            except ValueError:
                # Si el número no es numérico, generar uno nuevo
                pass
        
        return "000001"
    
    @staticmethod
    def obtener_cuenta_por_codigo(empresa, codigo):
        """
        Obtiene una cuenta contable por su código.
        
        Args:
            empresa: Instancia de Empresa
            codigo: Código de la cuenta
            
        Returns:
            CuentaContable: Cuenta encontrada
            
        Raises:
            CuentaContable.DoesNotExist: Si la cuenta no existe
        """
        return CuentaContable.objects.get(empresa=empresa, codigo=codigo, activa=True)
    
    @staticmethod
    @transaction.atomic
    def generar_asiento_venta(factura):
        """
        Genera el asiento contable para una factura de venta.
        
        Lógica contable:
        - Venta contado: Débito Caja/Banco, Crédito Ingresos, Crédito IVA por pagar
        - Venta crédito: Débito Clientes, Crédito Ingresos, Crédito IVA por pagar
        
        Args:
            factura: Instancia de Factura
            
        Returns:
            Asiento: Asiento contable generado
            
        Raises:
            Exception: Si no se pueden encontrar las cuentas necesarias
        """
        if factura.asiento_contable:
            # Ya tiene asiento generado, no duplicar
            return factura.asiento_contable
        
        empresa = factura.empresa
        
        # Crear el asiento
        asiento = Asiento.objects.create(
            empresa=empresa,
            numero_asiento=ServicioContabilidad.obtener_siguiente_numero_asiento(empresa),
            fecha_asiento=factura.fecha_factura,
            tipo_asiento='automatico',
            concepto=f"Venta según factura {factura.numero_factura} - {factura.cliente.razon_social}",
            documento_origen=f"FACTURA-{factura.numero_factura}",
            creado_por=factura.creado_por
        )
        
        try:
            # Obtener cuentas contables necesarias
            if factura.tipo_venta == 'contado':
                # Cuenta de caja o banco (débito)
                cuenta_caja = ServicioContabilidad.obtener_cuenta_por_codigo(empresa, '1105')  # Caja
            else:
                # Cuenta de clientes (débito)
                cuenta_clientes = ServicioContabilidad.obtener_cuenta_por_codigo(empresa, '1305')  # Clientes
            
            # Cuenta de ingresos (crédito)
            cuenta_ingresos = ServicioContabilidad.obtener_cuenta_por_codigo(empresa, '4135')  # Ingresos por ventas
            
            # Cuenta de IVA por pagar (crédito) - solo si hay impuestos
            cuenta_iva = None
            if factura.total_impuestos > 0:
                cuenta_iva = ServicioContabilidad.obtener_cuenta_por_codigo(empresa, '2408')  # IVA por pagar
            
        except CuentaContable.DoesNotExist as e:
            raise ValueError(f"No se encontró la cuenta contable necesaria: {str(e)}")
        
        # Crear partidas del asiento
        orden = 1
        
        # 1. Partida de débito (Caja/Banco o Clientes)
        if factura.tipo_venta == 'contado':
            Partida.objects.create(
                asiento=asiento,
                cuenta=cuenta_caja,
                concepto=f"Cobro factura {factura.numero_factura} - {factura.cliente.razon_social}",
                valor_debito=factura.total,
                valor_credito=Decimal('0.00'),
                orden=orden,
                tercero=factura.cliente
            )
        else:
            Partida.objects.create(
                asiento=asiento,
                cuenta=cuenta_clientes,
                concepto=f"Venta a crédito factura {factura.numero_factura} - {factura.cliente.razon_social}",
                valor_debito=factura.total,
                valor_credito=Decimal('0.00'),
                orden=orden,
                tercero=factura.cliente
            )
        orden += 1
        
        # 2. Partida de crédito (Ingresos)
        Partida.objects.create(
            asiento=asiento,
            cuenta=cuenta_ingresos,
            concepto=f"Venta según factura {factura.numero_factura}",
            valor_debito=Decimal('0.00'),
            valor_credito=factura.subtotal,
            orden=orden,
            tercero=factura.cliente
        )
        orden += 1
        
        # 3. Partida de crédito (IVA por pagar) - solo si hay impuestos
        if factura.total_impuestos > 0 and cuenta_iva:
            Partida.objects.create(
                asiento=asiento,
                cuenta=cuenta_iva,
                concepto=f"IVA factura {factura.numero_factura}",
                valor_debito=Decimal('0.00'),
                valor_credito=factura.total_impuestos,
                orden=orden,
                tercero=factura.cliente
            )
        
        # Calcular totales y confirmar asiento
        asiento.calcular_totales()
        asiento.estado = 'confirmado'
        asiento.confirmado_por = factura.creado_por
        asiento.fecha_confirmacion = timezone.now()
        asiento.save()
        
        # Actualizar saldos de las cuentas
        if factura.tipo_venta == 'contado':
            cuenta_caja.actualizar_saldos(debito=factura.total)
        else:
            cuenta_clientes.actualizar_saldos(debito=factura.total)
        
        cuenta_ingresos.actualizar_saldos(credito=factura.subtotal)
        
        if factura.total_impuestos > 0 and cuenta_iva:
            cuenta_iva.actualizar_saldos(credito=factura.total_impuestos)
        
        # Asociar el asiento a la factura
        factura.asiento_contable = asiento
        factura.save(update_fields=['asiento_contable'])
        
        return asiento
    
    @staticmethod
    @transaction.atomic
    def generar_asiento_cobro(pago):
        """
        Genera el asiento contable para un cobro a cliente.
        
        Lógica contable:
        - Débito: Caja/Banco
        - Crédito: Clientes
        
        Args:
            pago: Instancia de Pago (tipo cobro)
            
        Returns:
            Asiento: Asiento contable generado
            
        Raises:
            Exception: Si no se pueden encontrar las cuentas necesarias
        """
        if pago.asiento_contable:
            # Ya tiene asiento generado, no duplicar
            return pago.asiento_contable
        
        if pago.tipo_pago != 'cobro':
            raise ValueError("Este método solo aplica para cobros a clientes")
        
        empresa = pago.empresa
        
        # Crear el asiento
        asiento = Asiento.objects.create(
            empresa=empresa,
            numero_asiento=ServicioContabilidad.obtener_siguiente_numero_asiento(empresa),
            fecha_asiento=pago.fecha_pago,
            tipo_asiento='automatico',
            concepto=f"Cobro a cliente {pago.tercero.razon_social} - {pago.metodo_pago.nombre}",
            documento_origen=f"COBRO-{pago.numero_pago}",
            creado_por=pago.creado_por
        )
        
        try:
            # Obtener cuentas contables necesarias
            cuenta_caja = ServicioContabilidad.obtener_cuenta_por_codigo(empresa, '1105')  # Caja
            cuenta_clientes = ServicioContabilidad.obtener_cuenta_por_codigo(empresa, '1305')  # Clientes
            
        except CuentaContable.DoesNotExist as e:
            raise ValueError(f"No se encontró la cuenta contable necesaria: {str(e)}")
        
        # Crear partidas del asiento
        # 1. Partida de débito (Caja/Banco)
        Partida.objects.create(
            asiento=asiento,
            cuenta=cuenta_caja,
            concepto=f"Cobro de {pago.tercero.razon_social} - {pago.metodo_pago.nombre}",
            valor_debito=pago.valor,
            valor_credito=Decimal('0.00'),
            orden=1,
            tercero=pago.tercero
        )
        
        # 2. Partida de crédito (Clientes)
        concepto_credito = f"Abono a cuenta de {pago.tercero.razon_social}"
        if pago.factura:
            concepto_credito += f" - Factura {pago.factura.numero_factura}"
        
        Partida.objects.create(
            asiento=asiento,
            cuenta=cuenta_clientes,
            concepto=concepto_credito,
            valor_debito=Decimal('0.00'),
            valor_credito=pago.valor,
            orden=2,
            tercero=pago.tercero
        )
        
        # Calcular totales y confirmar asiento
        asiento.calcular_totales()
        asiento.estado = 'confirmado'
        asiento.confirmado_por = pago.creado_por
        asiento.fecha_confirmacion = timezone.now()
        asiento.save()
        
        # Actualizar saldos de las cuentas
        cuenta_caja.actualizar_saldos(debito=pago.valor)
        cuenta_clientes.actualizar_saldos(credito=pago.valor)
        
        # Asociar el asiento al pago
        pago.asiento_contable = asiento
        pago.save(update_fields=['asiento_contable'])
        
        return asiento
    
    @staticmethod
    @transaction.atomic
    def reversar_asiento(asiento_original, usuario, motivo="Reversión de asiento"):
        """
        Genera un asiento de reversión para anular un asiento existente.
        
        Args:
            asiento_original: Asiento a reversar
            usuario: Usuario que realiza la reversión
            motivo: Motivo de la reversión
            
        Returns:
            Asiento: Asiento de reversión generado
        """
        if asiento_original.estado != 'confirmado':
            raise ValueError("Solo se pueden reversar asientos confirmados")
        
        empresa = asiento_original.empresa
        
        # Crear el asiento de reversión
        asiento_reverso = Asiento.objects.create(
            empresa=empresa,
            numero_asiento=ServicioContabilidad.obtener_siguiente_numero_asiento(empresa),
            fecha_asiento=timezone.now().date(),
            tipo_asiento='automatico',
            concepto=f"REVERSIÓN - {asiento_original.concepto}",
            observaciones=f"Motivo: {motivo}. Reversa asiento {asiento_original.numero_asiento}",
            documento_origen=f"REV-{asiento_original.numero_asiento}",
            creado_por=usuario
        )
        
        # Crear partidas inversas
        for partida_original in asiento_original.partidas.all():
            Partida.objects.create(
                asiento=asiento_reverso,
                cuenta=partida_original.cuenta,
                concepto=f"REVERSIÓN - {partida_original.concepto}",
                # Invertir débitos y créditos
                valor_debito=partida_original.valor_credito,
                valor_credito=partida_original.valor_debito,
                orden=partida_original.orden,
                tercero=partida_original.tercero
            )
            
            # Actualizar saldos de las cuentas (inverso)
            partida_original.cuenta.actualizar_saldos(
                debito=partida_original.valor_credito,
                credito=partida_original.valor_debito
            )
        
        # Calcular totales y confirmar asiento de reversión
        asiento_reverso.calcular_totales()
        asiento_reverso.estado = 'confirmado'
        asiento_reverso.confirmado_por = usuario
        asiento_reverso.fecha_confirmacion = timezone.now()
        asiento_reverso.save()
        
        # Marcar el asiento original como anulado
        asiento_original.estado = 'anulado'
        asiento_original.observaciones += f"\n\nAnulado por asiento de reversión {asiento_reverso.numero_asiento}"
        asiento_original.save()
        
        return asiento_reverso


class ServicioPlanCuentas:
    """
    Servicio para gestionar el plan de cuentas.
    """
    
    @staticmethod
    def crear_plan_cuentas_basico(empresa, usuario):
        """
        Crea un plan de cuentas básico para una nueva empresa.
        
        Args:
            empresa: Instancia de Empresa
            usuario: Usuario que crea el plan de cuentas
        """
        cuentas_basicas = [
            # ACTIVOS
            {'codigo': '1', 'nombre': 'ACTIVO', 'naturaleza': 'D', 'tipo': 'ACTIVO', 'nivel': 1, 'acepta_mov': False},
            {'codigo': '11', 'nombre': 'ACTIVO CORRIENTE', 'naturaleza': 'D', 'tipo': 'ACTIVO', 'nivel': 2, 'acepta_mov': False, 'padre': '1'},
            {'codigo': '1105', 'nombre': 'CAJA', 'naturaleza': 'D', 'tipo': 'ACTIVO', 'nivel': 3, 'acepta_mov': True, 'padre': '11'},
            {'codigo': '1110', 'nombre': 'BANCOS', 'naturaleza': 'D', 'tipo': 'ACTIVO', 'nivel': 3, 'acepta_mov': True, 'padre': '11'},
            {'codigo': '1305', 'nombre': 'CLIENTES', 'naturaleza': 'D', 'tipo': 'ACTIVO', 'nivel': 3, 'acepta_mov': True, 'padre': '11'},
            
            # PASIVOS
            {'codigo': '2', 'nombre': 'PASIVO', 'naturaleza': 'C', 'tipo': 'PASIVO', 'nivel': 1, 'acepta_mov': False},
            {'codigo': '24', 'nombre': 'IMPUESTOS GRAVÁMENES Y TASAS', 'naturaleza': 'C', 'tipo': 'PASIVO', 'nivel': 2, 'acepta_mov': False, 'padre': '2'},
            {'codigo': '2408', 'nombre': 'IVA POR PAGAR', 'naturaleza': 'C', 'tipo': 'PASIVO', 'nivel': 3, 'acepta_mov': True, 'padre': '24'},
            
            # PATRIMONIO
            {'codigo': '3', 'nombre': 'PATRIMONIO', 'naturaleza': 'C', 'tipo': 'PATRIMONIO', 'nivel': 1, 'acepta_mov': False},
            {'codigo': '31', 'nombre': 'CAPITAL SOCIAL', 'naturaleza': 'C', 'tipo': 'PATRIMONIO', 'nivel': 2, 'acepta_mov': True, 'padre': '3'},
            
            # INGRESOS
            {'codigo': '4', 'nombre': 'INGRESOS', 'naturaleza': 'C', 'tipo': 'INGRESO', 'nivel': 1, 'acepta_mov': False},
            {'codigo': '41', 'nombre': 'INGRESOS OPERACIONALES', 'naturaleza': 'C', 'tipo': 'INGRESO', 'nivel': 2, 'acepta_mov': False, 'padre': '4'},
            {'codigo': '4135', 'nombre': 'COMERCIO AL POR MAYOR Y AL POR MENOR', 'naturaleza': 'C', 'tipo': 'INGRESO', 'nivel': 3, 'acepta_mov': True, 'padre': '41'},
            
            # GASTOS
            {'codigo': '5', 'nombre': 'GASTOS', 'naturaleza': 'D', 'tipo': 'GASTO', 'nivel': 1, 'acepta_mov': False},
            {'codigo': '51', 'nombre': 'GASTOS OPERACIONALES DE ADMINISTRACIÓN', 'naturaleza': 'D', 'tipo': 'GASTO', 'nivel': 2, 'acepta_mov': False, 'padre': '5'},
            {'codigo': '5105', 'nombre': 'GASTOS DE PERSONAL', 'naturaleza': 'D', 'tipo': 'GASTO', 'nivel': 3, 'acepta_mov': True, 'padre': '51'},
        ]
        
        cuentas_creadas = {}
        
        for cuenta_data in cuentas_basicas:
            cuenta_padre = None
            if 'padre' in cuenta_data:
                cuenta_padre = cuentas_creadas.get(cuenta_data['padre'])
            
            cuenta = CuentaContable.objects.create(
                empresa=empresa,
                codigo=cuenta_data['codigo'],
                nombre=cuenta_data['nombre'],
                naturaleza=cuenta_data['naturaleza'],
                tipo_cuenta=cuenta_data['tipo'],
                nivel=cuenta_data['nivel'],
                acepta_movimiento=cuenta_data['acepta_mov'],
                cuenta_padre=cuenta_padre
            )
            
            cuentas_creadas[cuenta_data['codigo']] = cuenta
        
        return cuentas_creadas
