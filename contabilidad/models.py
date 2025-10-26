from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Constante para evitar duplicación del literal 'empresas.Empresa'
EMPRESA_MODEL = 'empresas.Empresa'


class CuentaContable(models.Model):
    """
    Modelo para el plan de cuentas contables.
    Cada empresa tiene su propio plan de cuentas.
    """
    NATURALEZA_CHOICES = [
        ('D', 'Débito'),
        ('C', 'Crédito'),
    ]
    
    TIPO_CUENTA_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('PASIVO', 'Pasivo'),
        ('PATRIMONIO', 'Patrimonio'),
        ('INGRESO', 'Ingreso'),
        ('GASTO', 'Gasto'),
        ('COSTO', 'Costo'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información de la cuenta
    codigo = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{1,20}$',
                message='El código debe contener solo números'
            )
        ],
        verbose_name="Código",
        help_text="Código numérico de la cuenta (ej: 1105, 110505)"
    )
    
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la Cuenta"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    # Clasificación contable
    naturaleza = models.CharField(
        max_length=1,
        choices=NATURALEZA_CHOICES,
        verbose_name="Naturaleza",
        help_text="Naturaleza normal de la cuenta (Débito o Crédito)"
    )
    
    tipo_cuenta = models.CharField(
        max_length=15,
        choices=TIPO_CUENTA_CHOICES,
        verbose_name="Tipo de Cuenta"
    )
    
    # Jerarquía de cuentas
    cuenta_padre = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='subcuentas',
        verbose_name="Cuenta Padre"
    )
    
    nivel = models.PositiveIntegerField(
        default=1,
        verbose_name="Nivel",
        help_text="Nivel jerárquico de la cuenta (1=Mayor, 2=Submyor, etc.)"
    )
    
    # Control de movimientos
    acepta_movimiento = models.BooleanField(
        default=True,
        verbose_name="Acepta Movimiento",
        help_text="Si la cuenta puede tener partidas contables"
    )
    
    # Saldos
    saldo_inicial = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Saldo Inicial"
    )
    
    saldo_debito = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Saldo Débito"
    )
    
    saldo_credito = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Saldo Crédito"
    )
    
    # Estado
    activa = models.BooleanField(
        default=True,
        verbose_name="Cuenta Activa"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    class Meta:
        verbose_name = "Cuenta Contable"
        verbose_name_plural = "Cuentas Contables"
        unique_together = ['empresa', 'codigo']
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def saldo_actual(self):
        """
        Calcula el saldo actual de la cuenta basado en su naturaleza.
        """
        if self.naturaleza == 'D':
            # Cuentas de naturaleza débito: Saldo = Débitos - Créditos
            return self.saldo_inicial + self.saldo_debito - self.saldo_credito
        else:
            # Cuentas de naturaleza crédito: Saldo = Créditos - Débitos
            return self.saldo_inicial + self.saldo_credito - self.saldo_debito
    
    @property
    def saldo_deudor(self):
        """Retorna el saldo deudor si es positivo, 0 si es negativo"""
        saldo = self.saldo_actual
        return saldo if saldo > 0 else Decimal('0.00')
    
    @property
    def saldo_acreedor(self):
        """Retorna el saldo acreedor si es negativo, 0 si es positivo"""
        saldo = self.saldo_actual
        return abs(saldo) if saldo < 0 else Decimal('0.00')
    
    @property
    def codigo_completo(self):
        """Retorna el código con formato jerárquico"""
        return self.codigo
    
    def actualizar_saldos(self, debito=Decimal('0.00'), credito=Decimal('0.00')):
        """
        Actualiza los saldos de la cuenta.
        
        Args:
            debito: Valor a sumar al saldo débito
            credito: Valor a sumar al saldo crédito
        """
        self.saldo_debito += debito
        self.saldo_credito += credito
        self.save(update_fields=['saldo_debito', 'saldo_credito'])
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        # Validar que las cuentas padre no acepten movimiento
        if self.cuenta_padre and self.cuenta_padre.acepta_movimiento:
            if self.cuenta_padre.subcuentas.filter(acepta_movimiento=True).exists():
                raise ValidationError({
                    'cuenta_padre': 'La cuenta padre no puede aceptar movimiento si tiene subcuentas activas.'
                })


class Asiento(models.Model):
    """
    Modelo para gestionar asientos contables.
    """
    TIPO_ASIENTO_CHOICES = [
        ('manual', 'Manual'),
        ('automatico', 'Automático'),
    ]
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('confirmado', 'Confirmado'),
        ('anulado', 'Anulado'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        EMPRESA_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información del asiento
    numero_asiento = models.CharField(
        max_length=20,
        verbose_name="Número de Asiento",
        help_text="Número consecutivo del asiento"
    )
    
    fecha_asiento = models.DateField(
        verbose_name="Fecha del Asiento"
    )
    
    tipo_asiento = models.CharField(
        max_length=15,
        choices=TIPO_ASIENTO_CHOICES,
        default='manual',
        verbose_name="Tipo de Asiento"
    )
    
    concepto = models.CharField(
        max_length=300,
        verbose_name="Concepto",
        help_text="Descripción del asiento contable"
    )
    
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    
    # Totales del asiento
    total_debito = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total Débito"
    )
    
    total_credito = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Total Crédito"
    )
    
    # Estado y control
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default='borrador',
        verbose_name="Estado"
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
        related_name='asientos_creados',
        verbose_name="Creado Por"
    )
    
    confirmado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='asientos_confirmados',
        verbose_name="Confirmado Por"
    )
    
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Confirmación"
    )
    
    # Documento origen (si es automático)
    documento_origen = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Documento Origen",
        help_text="Referencia al documento que generó el asiento"
    )
    
    class Meta:
        verbose_name = "Asiento Contable"
        verbose_name_plural = "Asientos Contables"
        unique_together = ['empresa', 'numero_asiento']
        ordering = ['-fecha_asiento', '-numero_asiento']
    
    def __str__(self):
        return f"Asiento {self.numero_asiento} - {self.concepto}"
    
    def calcular_totales(self):
        """
        Calcula los totales del asiento basado en sus partidas.
        """
        partidas = self.partidas.all()
        
        total_debito = sum(p.valor_debito for p in partidas)
        total_credito = sum(p.valor_credito for p in partidas)
        
        self.total_debito = total_debito
        self.total_credito = total_credito
    
    @property
    def esta_cuadrado(self):
        """Verifica si el asiento está cuadrado (débitos = créditos)"""
        return self.total_debito == self.total_credito
    
    @property
    def puede_editarse(self):
        """Verifica si el asiento puede editarse"""
        return self.estado == 'borrador'
    
    @property
    def puede_confirmarse(self):
        """Verifica si el asiento puede confirmarse"""
        return (self.estado == 'borrador' and 
                self.partidas.exists() and 
                self.esta_cuadrado)
    
    @property
    def puede_anularse(self):
        """Verifica si el asiento puede anularse"""
        return self.estado == 'confirmado'
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        if self.estado == 'confirmado' and not self.esta_cuadrado:
            raise ValidationError(
                'No se puede confirmar un asiento que no esté cuadrado. '
                f'Débitos: ${self.total_debito}, Créditos: ${self.total_credito}'
            )


class Partida(models.Model):
    """
    Modelo para gestionar las partidas (líneas) de los asientos contables.
    """
    # Relación con el asiento
    asiento = models.ForeignKey(
        Asiento,
        on_delete=models.CASCADE,
        related_name='partidas',
        verbose_name="Asiento"
    )
    
    # Cuenta contable
    cuenta = models.ForeignKey(
        CuentaContable,
        on_delete=models.PROTECT,
        verbose_name="Cuenta Contable"
    )
    
    # Información de la partida
    concepto = models.CharField(
        max_length=300,
        verbose_name="Concepto",
        help_text="Descripción específica de la partida"
    )
    
    # Valores débito y crédito
    valor_debito = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Débito"
    )
    
    valor_credito = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Valor Crédito"
    )
    
    # Orden de la partida en el asiento
    orden = models.PositiveIntegerField(
        default=1,
        verbose_name="Orden"
    )
    
    # Información adicional
    tercero = models.ForeignKey(
        'catalogos.Tercero',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Tercero",
        help_text="Tercero relacionado con la partida (opcional)"
    )
    
    class Meta:
        verbose_name = "Partida Contable"
        verbose_name_plural = "Partidas Contables"
        ordering = ['asiento', 'orden']
    
    def __str__(self):
        if self.valor_debito > 0:
            return f"{self.cuenta.codigo} - Débito: ${self.valor_debito}"
        else:
            return f"{self.cuenta.codigo} - Crédito: ${self.valor_credito}"
    
    @property
    def valor_movimiento(self):
        """Retorna el valor del movimiento (débito o crédito)"""
        return self.valor_debito if self.valor_debito > 0 else self.valor_credito
    
    @property
    def tipo_movimiento(self):
        """Retorna el tipo de movimiento (D o C)"""
        return 'D' if self.valor_debito > 0 else 'C'
    
    def clean(self):
        """Validaciones personalizadas del modelo"""
        # Validar que solo uno de los valores sea mayor que cero
        if self.valor_debito > 0 and self.valor_credito > 0:
            raise ValidationError(
                'Una partida no puede tener valor en débito y crédito al mismo tiempo.'
            )
        
        if self.valor_debito == 0 and self.valor_credito == 0:
            raise ValidationError(
                'Una partida debe tener valor en débito o crédito.'
            )
        
        # Validar que la cuenta acepte movimiento
        if self.cuenta and not self.cuenta.acepta_movimiento:
            raise ValidationError({
                'cuenta': f'La cuenta {self.cuenta.codigo} - {self.cuenta.nombre} no acepta movimiento.'
            })
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para actualizar totales del asiento.
        """
        super().save(*args, **kwargs)
        
        # Recalcular totales del asiento
        if self.asiento:
            self.asiento.calcular_totales()
            self.asiento.save()
