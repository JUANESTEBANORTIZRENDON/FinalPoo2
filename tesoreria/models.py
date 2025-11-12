from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User


# Constantes para evitar duplicación de literales
EMPRESA_MODEL = 'empresas.Empresa'
VERBOSE_FECHA_CREACION = 'Fecha de Creación'
VERBOSE_ULTIMA_ACTUALIZACION = 'Última Actualización'


class Pago(models.Model):
    """
    Modelo para gestionar pagos (cobros a clientes y egresos a proveedores).
    """
    TIPO_PAGO_CHOICES = [
        ('cobro', 'Cobro a Cliente'),
        ('egreso', 'Egreso a Proveedor'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
        ('pagado', 'Pagado'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información básica del pago
    numero_pago = models.CharField(
        max_length=20,
        verbose_name="Número de Pago",
        help_text="Número consecutivo del pago"
    )
    
    fecha_pago = models.DateField(
        verbose_name="Fecha de Pago"
    )
    
    tipo_pago = models.CharField(
        max_length=10,
        choices=TIPO_PAGO_CHOICES,
        verbose_name="Tipo de Pago"
    )
    
    # Tercero (cliente o proveedor)
    tercero = models.ForeignKey(
        'catalogos.Tercero',
        on_delete=models.PROTECT,
        verbose_name="Cliente/Proveedor"
    )
    
    # Factura relacionada (opcional)
    factura = models.ForeignKey(
        'facturacion.Factura',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Factura Relacionada",
        help_text="Factura que se está pagando (opcional)"
    )
    
    # Método de pago
    metodo_pago = models.ForeignKey(
        'catalogos.MetodoPago',
        on_delete=models.PROTECT,
        verbose_name="Método de Pago"
    )
    
    # Cuenta bancaria (opcional)
    cuenta_bancaria = models.ForeignKey(
        'tesoreria.CuentaBancaria',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Cuenta Bancaria",
        help_text="Cuenta bancaria desde/hacia la que se realiza el pago"
    )
    
    # Información del pago
    valor = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor del Pago"
    )
    
    referencia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia",
        help_text="Número de cheque, referencia de transferencia, etc."
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # Estado y control
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Información del sistema
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VERBOSE_FECHA_CREACION
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name=VERBOSE_ULTIMA_ACTUALIZACION
    )
    
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='pagos_creados',
        verbose_name="Creado Por"
    )
    
    confirmado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='pagos_confirmados',
        verbose_name="Confirmado Por"
    )
    
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Confirmación"
    )
    
    # Relación con asiento contable
    asiento_contable = models.ForeignKey(
        'contabilidad.Asiento',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Asiento Contable"
    )
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        unique_together = ['empresa', 'numero_pago']
        ordering = ['-fecha_pago', '-numero_pago']
    
    def __str__(self):
        tipo_display = "Cobro" if self.tipo_pago == 'cobro' else "Egreso"
        return f"{tipo_display} {self.numero_pago} - {self.tercero.razon_social}"
    
    @property
    def puede_editarse(self):
        """Verifica si el pago puede editarse"""
        return self.estado == 'pendiente'
    
    @property
    def puede_activarse(self):
        """Verifica si el pago puede activarse"""
        return self.estado == 'pendiente'
    
    @property
    def puede_marcarse_pagado(self):
        """Verifica si el pago puede marcarse como pagado"""
        return self.estado == 'activo'
    
    @property
    def es_cobro(self):
        """Verifica si es un cobro a cliente"""
        return self.tipo_pago == 'cobro'
    
    @property
    def es_egreso(self):
        """Verifica si es un egreso a proveedor"""
        return self.tipo_pago == 'egreso'
    
    def disminuir_stock(self):
        """
        Disminuye el stock de los productos en el cobro.
        Se ejecuta cuando el cobro se marca como pagado.
        """
        for detalle in self.detalles.all():
            producto = detalle.producto
            
            # Solo disminuir stock si el producto es inventariable
            if producto.inventariable:
                # Verificar que haya stock suficiente
                if producto.stock_actual >= detalle.cantidad:
                    producto.stock_actual -= detalle.cantidad
                    producto.save()
                else:
                    # Si no hay stock suficiente, lanzar excepción
                    from django.core.exceptions import ValidationError
                    raise ValidationError(
                        f'Stock insuficiente para {producto.nombre}. '
                        f'Disponible: {producto.stock_actual}, '
                        f'Requerido: {detalle.cantidad}'
                    )
    
    def clean(self):
        """
        Validaciones personalizadas del modelo.
        """
        from django.core.exceptions import ValidationError
        
        # Validar que el tercero sea del tipo correcto
        if self.tipo_pago == 'cobro' and self.tercero and not self.tercero.es_cliente:
            raise ValidationError({
                'tercero': 'Para cobros, debe seleccionar un cliente.'
            })
        
        if self.tipo_pago == 'egreso' and self.tercero and not self.tercero.es_proveedor:
            raise ValidationError({
                'tercero': 'Para egresos, debe seleccionar un proveedor.'
            })
        
        # Validar que la factura corresponda al tercero
        if self.factura and self.factura.cliente != self.tercero:
            raise ValidationError({
                'factura': 'La factura debe corresponder al tercero seleccionado.'
            })
        
        # Validar que la referencia sea obligatoria si el método la requiere
        if self.metodo_pago and self.metodo_pago.requiere_referencia and not self.referencia:
            raise ValidationError({
                'referencia': f'El método de pago {self.metodo_pago.nombre} requiere una referencia.'
            })


class CuentaBancaria(models.Model):
    """
    Modelo para gestionar cuentas bancarias de la empresa.
    """
    TIPO_CUENTA_CHOICES = [
        ('ahorros', 'Cuenta de Ahorros'),
        ('corriente', 'Cuenta Corriente'),
        ('caja', 'Caja General'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información de la cuenta
    codigo = models.CharField(
        max_length=10,
        verbose_name="Código",
        help_text="Código interno de la cuenta"
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre de la Cuenta"
    )
    
    tipo_cuenta = models.CharField(
        max_length=15,
        choices=TIPO_CUENTA_CHOICES,
        verbose_name="Tipo de Cuenta"
    )
    
    numero_cuenta = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Número de Cuenta",
        help_text="Número de cuenta bancaria (si aplica)"
    )
    
    banco = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Banco",
        help_text="Nombre del banco (si aplica)"
    )
    
    # Saldo actual
    saldo_actual = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Saldo Actual"
    )
    
    # Estado
    activa = models.BooleanField(
        default=True,
        verbose_name="Cuenta Activa"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VERBOSE_FECHA_CREACION
    )
    
    # Relación con cuenta contable
    cuenta_contable = models.ForeignKey(
        'contabilidad.CuentaContable',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Cuenta Contable Asociada"
    )
    
    class Meta:
        verbose_name = "Cuenta Bancaria"
        verbose_name_plural = "Cuentas Bancarias"
        unique_together = ['empresa', 'codigo']
        ordering = ['nombre']
    
    def __str__(self):
        if self.banco:
            return f"{self.nombre} - {self.banco} ({self.numero_cuenta})"
        return f"{self.nombre} ({self.codigo})"
    
    def actualizar_saldo(self, valor, es_debito=True):
        """
        Actualiza el saldo de la cuenta.
        
        Args:
            valor: Valor a sumar o restar
            es_debito: True para débito (suma), False para crédito (resta)
        """
        if es_debito:
            self.saldo_actual += valor
        else:
            self.saldo_actual -= valor
        
        self.save(update_fields=['saldo_actual'])
    
    @property
    def saldo_formateado(self):
        """Retorna el saldo con formato de moneda"""
        return f"${self.saldo_actual:,.2f}"


class PagoDetalle(models.Model):
    """
    Modelo para gestionar los detalles (productos) de un pago/cobro.
    """
    # Relación con el pago
    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Pago"
    )
    
    # Producto
    producto = models.ForeignKey(
        'catalogos.Producto',
        on_delete=models.PROTECT,
        verbose_name="Producto"
    )
    
    # Cantidad y valores
    cantidad = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Unitario"
    )
    
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Subtotal",
        help_text="Cantidad × Precio Unitario"
    )
    
    # Información del sistema
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VERBOSE_FECHA_CREACION
    )
    
    class Meta:
        verbose_name = "Detalle de Pago"
        verbose_name_plural = "Detalles de Pago"
        ordering = ['id']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} × ${self.precio_unitario}"
    
    def clean(self):
        """
        Validaciones personalizadas del detalle.
        """
        from django.core.exceptions import ValidationError
        
        # Validar stock disponible solo para productos inventariables
        if self.producto and self.producto.inventariable:
            if self.cantidad > self.producto.stock_actual:
                raise ValidationError({
                    'cantidad': f'Stock insuficiente para {self.producto.nombre}. '
                               f'Disponible: {self.producto.stock_actual}, '
                               f'Solicitado: {self.cantidad}'
                })
    
    def save(self, *args, **kwargs):
        """Calcular subtotal antes de guardar"""
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class ExtractoBancario(models.Model):
    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT, related_name='extractos')
    fecha = models.DateField()
    descripcion = models.CharField(max_length=255)
    referencia = models.CharField(max_length=128, blank=True)
    valor = models.DecimalField(max_digits=15, decimal_places=2)
    conciliado = models.BooleanField(default=False)
    pago = models.ForeignKey('tesoreria.Pago', null=True, blank=True, on_delete=models.SET_NULL, related_name='conciliaciones')

    class Meta:
        verbose_name = 'Extracto Bancario'
        verbose_name_plural = 'Extractos Bancarios'
        ordering = ['-fecha', '-id']

    def __str__(self):
        return f"{self.fecha} {self.descripcion} {self.valor}"
