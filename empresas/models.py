from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from decimal import Decimal


class Empresa(models.Model):
    """
    Modelo para gestionar empresas en el sistema contable.
    Cada empresa tiene su propio conjunto de datos contables.
    """
    TIPO_EMPRESA_CHOICES = [
        ('SAS', 'Sociedad por Acciones Simplificada'),
        ('LTDA', 'Sociedad Limitada'),
        ('SA', 'Sociedad Anónima'),
        ('ESAL', 'Entidad Sin Ánimo de Lucro'),
        ('PERSONA_NATURAL', 'Persona Natural'),
        ('OTRO', 'Otro'),
    ]
    
    REGIMEN_CHOICES = [
        ('COMUN', 'Régimen Común'),
        ('SIMPLIFICADO', 'Régimen Simplificado'),
        ('ESPECIAL', 'Régimen Especial'),
    ]
    
    # Información básica
    nit = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{9,11}-\d{1}$',
                message='Formato NIT: 123456789-0'
            )
        ],
        verbose_name="NIT",
        help_text="Número de Identificación Tributaria con dígito de verificación"
    )
    
    razon_social = models.CharField(
        max_length=200,
        verbose_name="Razón Social"
    )
    
    nombre_comercial = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre Comercial"
    )
    
    tipo_empresa = models.CharField(
        max_length=20,
        choices=TIPO_EMPRESA_CHOICES,
        default='SAS',
        verbose_name="Tipo de Empresa"
    )
    
    # Información tributaria
    regimen_tributario = models.CharField(
        max_length=15,
        choices=REGIMEN_CHOICES,
        default='COMUN',
        verbose_name="Régimen Tributario"
    )
    
    responsable_iva = models.BooleanField(
        default=True,
        verbose_name="Responsable de IVA"
    )
    
    gran_contribuyente = models.BooleanField(
        default=False,
        verbose_name="Gran Contribuyente"
    )
    
    autorretenedor = models.BooleanField(
        default=False,
        verbose_name="Autorretenedor"
    )
    
    # Información de contacto
    direccion = models.TextField(
        max_length=300,
        verbose_name="Dirección"
    )
    
    ciudad = models.CharField(
        max_length=100,
        verbose_name="Ciudad"
    )
    
    departamento = models.CharField(
        max_length=100,
        default='Cundinamarca',
        verbose_name="Departamento"
    )
    
    telefono = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?57?[0-9]{7,12}$',
                message='Formato: +5713001234567 o 13001234567'
            )
        ],
        verbose_name="Teléfono"
    )
    
    email = models.EmailField(
        verbose_name="Email Corporativo"
    )
    
    sitio_web = models.URLField(
        blank=True,
        verbose_name="Sitio Web"
    )
    
    # Información contable
    moneda_base = models.CharField(
        max_length=3,
        default='COP',
        verbose_name="Moneda Base",
        help_text="Código ISO de la moneda (COP, USD, EUR)"
    )
    
    periodo_contable = models.CharField(
        max_length=10,
        default='ANUAL',
        choices=[
            ('MENSUAL', 'Mensual'),
            ('BIMESTRAL', 'Bimestral'),
            ('TRIMESTRAL', 'Trimestral'),
            ('SEMESTRAL', 'Semestral'),
            ('ANUAL', 'Anual'),
        ],
        verbose_name="Período Contable"
    )
    
    # Configuración del sistema
    activa = models.BooleanField(
        default=True,
        verbose_name="Empresa Activa"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    # Usuario que creó la empresa (propietario)
    propietario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='empresas_propias',
        verbose_name="Propietario"
    )
    
    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ['razon_social']
    
    def __str__(self):
        return f"{self.razon_social} ({self.nit})"
    
    @property
    def nit_formateado(self):
        """Retorna el NIT con formato de puntos"""
        if self.nit:
            nit_sin_dv = self.nit.split('-')[0]
            dv = self.nit.split('-')[1]
            # Formatear con puntos: 123.456.789-0
            nit_formateado = f"{nit_sin_dv[:-6]}.{nit_sin_dv[-6:-3]}.{nit_sin_dv[-3:]}-{dv}"
            return nit_formateado
        return self.nit


class PerfilEmpresa(models.Model):
    """
    Modelo para gestionar los roles de usuarios en cada empresa.
    Un usuario puede tener diferentes roles en diferentes empresas.
    """
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('contador', 'Contador'),
        ('operador', 'Operador'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='perfiles',
        verbose_name="Empresa"
    )
    
    rol = models.CharField(
        max_length=10,
        choices=ROL_CHOICES,
        verbose_name="Rol en la Empresa"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Perfil Activo"
    )
    
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Asignación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    # Usuario que asignó este rol
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='perfiles_asignados',
        verbose_name="Asignado Por"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuario en Empresa"
        verbose_name_plural = "Perfiles de Usuarios en Empresas"
        unique_together = ['usuario', 'empresa']
        ordering = ['empresa__razon_social', 'usuario__username']
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.empresa.razon_social} ({self.get_rol_display()})"
    
    @property
    def puede_administrar(self):
        """Verifica si el usuario puede administrar la empresa"""
        return self.rol == 'admin'
    
    @property
    def puede_confirmar_documentos(self):
        """Verifica si el usuario puede confirmar documentos contables"""
        return self.rol in ['admin', 'contador']
    
    @property
    def solo_lectura_reportes(self):
        """Verifica si el usuario solo puede ver reportes básicos"""
        return self.rol == 'operador'


class EmpresaActiva(models.Model):
    """
    Modelo para gestionar qué empresa está activa para cada usuario en su sesión.
    Esto permite que un usuario trabaje con una empresa específica a la vez.
    """
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        related_name='empresa_activa_sesion'
    )
    
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        verbose_name="Empresa Activa"
    )
    
    fecha_seleccion = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de Selección"
    )
    
    class Meta:
        verbose_name = "Empresa Activa por Usuario"
        verbose_name_plural = "Empresas Activas por Usuario"
    
    def __str__(self):
        return f"{self.usuario.username} -> {self.empresa.razon_social}"
