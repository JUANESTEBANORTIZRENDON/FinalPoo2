from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class PerfilUsuario(models.Model):
    """
    Perfil extendido del usuario con información adicional
    para el sistema contable colombiano
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PP', 'Pasaporte'),
        ('NIT', 'NIT (Número de Identificación Tributaria)'),
    ]
    
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
        ('N', 'Prefiero no decir'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('S', 'Soltero/a'),
        ('C', 'Casado/a'),
        ('U', 'Unión Libre'),
        ('D', 'Divorciado/a'),
        ('V', 'Viudo/a'),
    ]
    
    # Relación uno a uno con User
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        related_name='perfil'
    )
    
    # Información personal
    tipo_documento = models.CharField(
        max_length=3,
        choices=TIPO_DOCUMENTO_CHOICES,
        default='CC',
        verbose_name="Tipo de Documento"
    )
    
    numero_documento = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\d{6,20}$',
                message='El número de documento debe contener solo números (6-20 dígitos)'
            )
        ],
        verbose_name="Número de Documento",
        help_text="Número de identificación sin puntos ni espacios"
    )
    
    telefono = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?57?[0-9]{10,12}$',
                message='Formato: +573001234567 o 3001234567'
            )
        ],
        verbose_name="Teléfono",
        help_text="Número de teléfono celular colombiano"
    )
    
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de Nacimiento"
    )
    
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        blank=True,
        verbose_name="Género"
    )
    
    estado_civil = models.CharField(
        max_length=1,
        choices=ESTADO_CIVIL_CHOICES,
        blank=True,
        verbose_name="Estado Civil"
    )
    
    # Información de contacto
    direccion = models.TextField(
        max_length=200,
        blank=True,
        verbose_name="Dirección",
        help_text="Dirección completa de residencia"
    )
    
    ciudad = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ciudad"
    )
    
    departamento = models.CharField(
        max_length=100,
        default='Cundinamarca',
        verbose_name="Departamento"
    )
    
    pais = models.CharField(
        max_length=100,
        default='Colombia',
        verbose_name="País"
    )
    
    codigo_postal = models.CharField(
        max_length=10,
        blank=True,
        verbose_name="Código Postal"
    )
    
    # Información profesional
    profesion = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Profesión"
    )
    
    empresa = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Empresa"
    )
    
    cargo = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cargo"
    )
    
    # Información del sistema
    acepta_terminos = models.BooleanField(
        default=False,
        verbose_name="Acepta Términos y Condiciones"
    )
    
    acepta_politica_privacidad = models.BooleanField(
        default=False,
        verbose_name="Acepta Política de Privacidad"
    )
    
    recibir_notificaciones = models.BooleanField(
        default=True,
        verbose_name="Recibir Notificaciones por Email"
    )
    
    # Metadatos
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name="Perfil Activo"
    )
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} ({self.numero_documento})"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        return self.usuario.get_full_name() or self.usuario.username
    
    @property
    def documento_completo(self):
        """Retorna tipo y número de documento"""
        return f"{self.get_tipo_documento_display()} {self.numero_documento}"
    
    @property
    def edad(self):
        """Calcula la edad basada en la fecha de nacimiento"""
        if self.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Señal para crear automáticamente un perfil cuando se crea un usuario
    """
    if created:
        PerfilUsuario.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """
    Señal para guardar el perfil cuando se guarda el usuario
    """
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
