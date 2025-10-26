from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User


# Constante para evitar duplicación del literal 'empresas.Empresa'
EMPRESA_MODEL = 'empresas.Empresa'


class Factura(models.Model):
    """
    Modelo para gestionar facturas de venta.
    """
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('confirmada', 'Confirmada'),
        ('anulada', 'Anulada'),
    ]
    
    TIPO_VENTA_CHOICES = [
        ('contado', 'Contado'),
        ('credito', 'Crédito'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información de la factura
    numero_factura = models.CharField(
        max_length=20,
        verbose_name="Número de Factura",
        help_text="Número consecutivo de la factura"
    )
    
    fecha_factura = models.DateField(
        verbose_name="Fecha de Factura"
    )
    
    fecha_vencimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Vencimiento",
        help_text="Solo para ventas a crédito"
    )
    
    # Cliente
    cliente = models.ForeignKey(
        'catalogos.Tercero',
        on_delete=models.PROTECT,
        limit_choices_to={'tipo_tercero__in': ['cliente', 'ambos']},
        verbose_name="Cliente"
    )
    
    # Tipo de venta
    tipo_venta = models.CharField(
        max_length=10,
        choices=TIPO_VENTA_CHOICES,
        default='contado',
        verbose_name="Tipo de Venta"
    )
    
    # Método de pago (solo para ventas de contado)
    metodo_pago = models.ForeignKey(
        'catalogos.MetodoPago',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Método de Pago",
        help_text="Solo para ventas de contado"
    )
    
    # Totales de la factura
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Subtotal"
    )
    
    total_impuestos = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total Impuestos"
    )
    
    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total"
    )
    
    # Estado y control
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='borrador',
        verbose_name="Estado"
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # Información del sistema
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='facturas_creadas',
        verbose_name="Creado Por"
    )
    
    confirmado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='facturas_confirmadas',
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
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        unique_together = ['empresa', 'numero_factura']
        ordering = ['-fecha_factura', '-numero_factura']
    
    def __str__(self):
        return f"Factura {self.numero_factura} - {self.cliente.razon_social}"
    
    def calcular_totales(self):
        """
        Calcula los totales de la factura basado en sus detalles.
        """
        detalles = self.detalles.all()
        
        subtotal = Decimal('0.00')
        total_impuestos = Decimal('0.00')
        
        for detalle in detalles:
            subtotal += detalle.subtotal
            total_impuestos += detalle.valor_impuesto
        
        self.subtotal = subtotal
        self.total_impuestos = total_impuestos
        self.total = subtotal + total_impuestos
    
    @property
    def puede_editarse(self):
        """Verifica si la factura puede editarse"""
        return self.estado == 'borrador'
    
    @property
    def puede_confirmarse(self):
        """Verifica si la factura puede confirmarse"""
        return self.estado == 'borrador' and self.detalles.exists()
    
    @property
    def puede_anularse(self):
        """Verifica si la factura puede anularse"""
        return self.estado == 'confirmada'


class FacturaDetalle(models.Model):
    """
    Modelo para gestionar los detalles (líneas) de las facturas.
    """
    # Relación con la factura
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name="Factura"
    )
    
    # Producto o servicio
    producto = models.ForeignKey(
        'catalogos.Producto',
        on_delete=models.PROTECT,
        verbose_name="Producto/Servicio"
    )
    
    # Información del detalle
    descripcion = models.CharField(
        max_length=300,
        verbose_name="Descripción",
        help_text="Descripción del producto/servicio en la factura"
    )
    
    cantidad = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Cantidad"
    )
    
    precio_unitario = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio Unitario"
    )
    
    # Impuesto aplicado
    impuesto = models.ForeignKey(
        'catalogos.Impuesto',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Impuesto"
    )
    
    porcentaje_impuesto = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="% Impuesto"
    )
    
    # Totales calculados
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Subtotal"
    )
    
    valor_impuesto = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Impuesto"
    )
    
    total_linea = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total Línea"
    )
    
    # Orden de la línea en la factura
    orden = models.PositiveIntegerField(
        default=1,
        verbose_name="Orden"
    )
    
    class Meta:
        verbose_name = "Detalle de Factura"
        verbose_name_plural = "Detalles de Facturas"
        ordering = ['factura', 'orden']
    
    def __str__(self):
        return f"{self.factura.numero_factura} - {self.producto.nombre}"
    
    def calcular_totales(self):
        """
        Calcula los totales de la línea de detalle.
        """
        # Calcular subtotal
        self.subtotal = (self.cantidad * self.precio_unitario).quantize(Decimal('0.01'))
        
        # Calcular impuesto
        if self.impuesto and self.porcentaje_impuesto > 0:
            self.valor_impuesto = (self.subtotal * self.porcentaje_impuesto / 100).quantize(Decimal('0.01'))
        else:
            self.valor_impuesto = Decimal('0.00')
        
        # Calcular total de la línea
        self.total_linea = self.subtotal + self.valor_impuesto
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para calcular totales automáticamente.
        """
        # Si hay un impuesto asociado, usar su porcentaje
        if self.impuesto:
            self.porcentaje_impuesto = self.impuesto.porcentaje
        
        # Calcular totales
        self.calcular_totales()
        
        super().save(*args, **kwargs)
        
        # Recalcular totales de la factura
        if self.factura:
            self.factura.calcular_totales()
            self.factura.save()
