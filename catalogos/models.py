from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal


# Constantes para evitar duplicación de literales
EMPRESA_MODEL = 'empresas.Empresa'
VN_CODIGO = 'Código'
VN_FECHA_CREACION = 'Fecha de Creación'


class Tercero(models.Model):
    """
    Modelo para gestionar terceros (clientes y proveedores).
    """
    TIPO_TERCERO_CHOICES = [
        ('cliente', 'Cliente'),
        ('proveedor', 'Proveedor'),
        ('ambos', 'Cliente y Proveedor'),
    ]
    
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PP', 'Pasaporte'),
        ('NIT', 'NIT (Número de Identificación Tributaria)'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información básica
    tipo_tercero = models.CharField(
        max_length=10,
        choices=TIPO_TERCERO_CHOICES,
        verbose_name="Tipo de Tercero"
    )
    
    tipo_documento = models.CharField(
        max_length=3,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='CC',
        verbose_name="Tipo de Documento"
    )
    
    numero_documento = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\d{6,20}$',
                message='El número de documento debe contener solo números (6-20 dígitos)'
            )
        ],
        verbose_name="Número de Documento",
        help_text="Número de identificación sin puntos ni espacios"
    )
    
    razon_social = models.CharField(
        max_length=200,
        verbose_name="Razón Social / Nombre Completo"
    )
    
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre Comercial"
    )
    
    # Información de contacto
    direccion = models.TextField(
        max_length=300,
        blank=True,
        verbose_name="Dirección"
    )
    
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad"
    )
    
    departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Departamento"
    )
    
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono",
        help_text="Número de teléfono o celular"
    )
    
    email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    
    # Información comercial
    activo = models.BooleanField(
        default=True,
        verbose_name="Tercero Activo"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VN_FECHA_CREACION
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    class Meta:
        verbose_name = "Tercero"
        verbose_name_plural = "Terceros"
        unique_together = ['empresa', 'numero_documento']
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.razon_social} ({self.numero_documento})"
    
    @property
    def es_cliente(self):
        return self.tipo_tercero in ['cliente', 'ambos']
    
    @property
    def es_proveedor(self):
        return self.tipo_tercero in ['proveedor', 'ambos']


class Impuesto(models.Model):
    """
    Modelo para gestionar impuestos (IVA, ICA, Retenciones, etc.).
    """
    TIPO_IMPUESTO_CHOICES = [
        ('IVA', 'IVA (Impuesto al Valor Agregado)'),
        ('ICA', 'ICA (Impuesto de Industria y Comercio)'),
        ('RETEFUENTE', 'Retención en la Fuente'),
        ('RETEIVA', 'Retención de IVA'),
        ('RETEICA', 'Retención de ICA'),
        ('OTRO', 'Otro Impuesto'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información del impuesto
    codigo = models.CharField(
        max_length=10,
        verbose_name=VN_CODIGO,
        help_text="Código interno del impuesto"
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Impuesto"
    )
    
    tipo_impuesto = models.CharField(
        max_length=15,
        choices=TIPO_IMPUESTO_CHOICES,
        verbose_name="Tipo de Impuesto"
    )
    
    porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        verbose_name="Porcentaje (%)",
        help_text="Porcentaje del impuesto (ej: 19.00 para IVA del 19%)"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Impuesto Activo"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VN_FECHA_CREACION
    )
    
    class Meta:
        verbose_name = "Impuesto"
        verbose_name_plural = "Impuestos"
        unique_together = ['empresa', 'codigo']
        ordering = ['tipo_impuesto', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"
    
    def calcular_impuesto(self, base):
        """Calcula el valor del impuesto sobre una base dada"""
        return (base * self.porcentaje / 100).quantize(Decimal('0.01'))


class MetodoPago(models.Model):
    """
    Modelo para gestionar métodos de pago.
    """
    TIPO_METODO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia Bancaria'),
        ('CHEQUE', 'Cheque'),
        ('TARJETA_CREDITO', 'Tarjeta de Crédito'),
        ('TARJETA_DEBITO', 'Tarjeta de Débito'),
        ('CONSIGNACION', 'Consignación'),
        ('OTRO', 'Otro'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información del método de pago
    codigo = models.CharField(
        max_length=10,
        verbose_name=VN_CODIGO,
        help_text="Código interno del método de pago"
    )
    
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre del Método de Pago"
    )
    
    tipo_metodo = models.CharField(
        max_length=20,
        choices=TIPO_METODO_CHOICES,
        verbose_name="Tipo de Método"
    )
    
    requiere_referencia = models.BooleanField(
        default=False,
        verbose_name="Requiere Referencia",
        help_text="Si requiere número de cheque, referencia de transferencia, etc."
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Método Activo"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VN_FECHA_CREACION
    )
    
    class Meta:
        verbose_name = "Método de Pago"
        verbose_name_plural = "Métodos de Pago"
        unique_together = ['empresa', 'codigo']
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_metodo_display()})"


class Producto(models.Model):
    """
    Modelo para gestionar productos y servicios.
    """
    TIPO_PRODUCTO_CHOICES = [
        ('producto', 'Producto'),
        ('servicio', 'Servicio'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información básica
    codigo = models.CharField(
        max_length=20,
        verbose_name="Código",
        help_text="Código interno del producto/servicio"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    tipo_producto = models.CharField(
        max_length=10,
        choices=TIPO_PRODUCTO_CHOICES,
        default='producto',
        verbose_name="Tipo"
    )
    
    # Información comercial
    precio_venta = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio de Venta"
    )
    
    precio_costo = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Precio de Costo",
        blank=True
    )
    
    # Impuestos
    impuesto = models.ForeignKey(
        Impuesto,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Impuesto Aplicable"
    )
    
    # Control de inventario
    inventariable = models.BooleanField(
        default=True,
        verbose_name="Maneja Inventario",
        help_text="Si el producto maneja control de inventario"
    )
    
    stock_actual = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Actual"
    )
    
    stock_minimo = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Stock Mínimo"
    )
    
    # Estado
    activo = models.BooleanField(
        default=True,
        verbose_name="Producto Activo"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name=VN_FECHA_CREACION
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        unique_together = ['empresa', 'codigo']
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def precio_con_impuesto(self):
        """Calcula el precio de venta incluyendo impuestos"""
        if self.impuesto:
            impuesto_valor = self.impuesto.calcular_impuesto(self.precio_venta)
            return self.precio_venta + impuesto_valor
        return self.precio_venta
    
    @property
    def margen_utilidad(self):
        """Calcula el margen de utilidad en porcentaje"""
        if self.precio_costo > 0 and self.precio_venta > 0:
            margen = ((self.precio_venta - self.precio_costo) / self.precio_costo * 100)
            return margen.quantize(Decimal('0.01'))
        return Decimal('0.00')
    
    @property
    def requiere_reposicion(self):
        """Verifica si el producto requiere reposición de stock"""
        return self.inventariable and self.stock_actual <= self.stock_minimo
