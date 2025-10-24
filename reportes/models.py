from django.db import models
from django.contrib.auth.models import User


class ReporteGenerado(models.Model):
    """
    Modelo para gestionar el historial de reportes generados.
    Permite llevar un registro de qué reportes se han generado y cuándo.
    """
    TIPO_REPORTE_CHOICES = [
        ('diario', 'Libro Diario'),
        ('mayor', 'Libro Mayor'),
        ('balance_comprobacion', 'Balance de Comprobación'),
        ('estado_resultados', 'Estado de Resultados (PyG)'),
        ('balance_general', 'Balance General'),
        ('flujo_efectivo', 'Flujo de Efectivo'),
    ]
    
    FORMATO_CHOICES = [
        ('html', 'HTML'),
        ('csv', 'CSV'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
    ]
    
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información del reporte
    tipo_reporte = models.CharField(
        max_length=25,
        choices=TIPO_REPORTE_CHOICES,
        verbose_name="Tipo de Reporte"
    )
    
    nombre_reporte = models.CharField(
        max_length=200,
        verbose_name="Nombre del Reporte"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    # Parámetros del reporte
    fecha_inicio = models.DateField(
        verbose_name="Fecha de Inicio"
    )
    
    fecha_fin = models.DateField(
        verbose_name="Fecha de Fin"
    )
    
    parametros_adicionales = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Parámetros Adicionales",
        help_text="Parámetros específicos del reporte en formato JSON"
    )
    
    # Información de generación
    formato_generado = models.CharField(
        max_length=10,
        choices=FORMATO_CHOICES,
        verbose_name="Formato Generado"
    )
    
    fecha_generacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Generación"
    )
    
    generado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Generado Por"
    )
    
    # Estadísticas del reporte
    numero_registros = models.PositiveIntegerField(
        default=0,
        verbose_name="Número de Registros",
        help_text="Cantidad de registros incluidos en el reporte"
    )
    
    tiempo_generacion = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        verbose_name="Tiempo de Generación (segundos)"
    )
    
    # Archivo generado (opcional)
    archivo_generado = models.FileField(
        upload_to='reportes/%Y/%m/',
        null=True,
        blank=True,
        verbose_name="Archivo Generado"
    )
    
    class Meta:
        verbose_name = "Reporte Generado"
        verbose_name_plural = "Reportes Generados"
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"{self.get_tipo_reporte_display()} - {self.fecha_inicio} a {self.fecha_fin}"
    
    @property
    def periodo_reporte(self):
        """Retorna el período del reporte en formato legible"""
        if self.fecha_inicio == self.fecha_fin:
            return f"Al {self.fecha_fin.strftime('%d/%m/%Y')}"
        else:
            return f"Del {self.fecha_inicio.strftime('%d/%m/%Y')} al {self.fecha_fin.strftime('%d/%m/%Y')}"


class ConfiguracionReporte(models.Model):
    """
    Modelo para gestionar configuraciones predefinidas de reportes.
    Permite a los usuarios guardar configuraciones frecuentes.
    """
    # Relación con empresa (multi-tenant)
    empresa = models.ForeignKey(
        'empresas.Empresa',
        on_delete=models.CASCADE,
        verbose_name="Empresa"
    )
    
    # Información de la configuración
    nombre = models.CharField(
        max_length=100,
        verbose_name="Nombre de la Configuración"
    )
    
    tipo_reporte = models.CharField(
        max_length=25,
        choices=ReporteGenerado.TIPO_REPORTE_CHOICES,
        verbose_name="Tipo de Reporte"
    )
    
    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    
    # Configuración guardada
    configuracion = models.JSONField(
        default=dict,
        verbose_name="Configuración",
        help_text="Configuración del reporte en formato JSON"
    )
    
    # Control de acceso
    es_publica = models.BooleanField(
        default=False,
        verbose_name="Es Pública",
        help_text="Si otros usuarios de la empresa pueden usar esta configuración"
    )
    
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Creado Por"
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )
    
    # Estadísticas de uso
    veces_utilizada = models.PositiveIntegerField(
        default=0,
        verbose_name="Veces Utilizada"
    )
    
    ultima_utilizacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Utilización"
    )
    
    class Meta:
        verbose_name = "Configuración de Reporte"
        verbose_name_plural = "Configuraciones de Reportes"
        unique_together = ['empresa', 'nombre', 'creado_por']
        ordering = ['tipo_reporte', 'nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_reporte_display()})"
    
    def incrementar_uso(self):
        """Incrementa el contador de uso y actualiza la fecha de última utilización"""
        from django.utils import timezone
        self.veces_utilizada += 1
        self.ultima_utilizacion = timezone.now()
        self.save(update_fields=['veces_utilizada', 'ultima_utilizacion'])
