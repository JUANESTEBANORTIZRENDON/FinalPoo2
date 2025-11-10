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
        ("SAS", "Sociedad por Acciones Simplificada"),
        ("LTDA", "Sociedad Limitada"),
        ("SA", "Sociedad Anónima"),
        ("ESAL", "Entidad Sin Ánimo de Lucro"),
        ("PERSONA_NATURAL", "Persona Natural"),
        ("OTRO", "Otro"),
    ]

    REGIMEN_CHOICES = [
        ("COMUN", "Régimen Común"),
        ("SIMPLIFICADO", "Régimen Simplificado"),
        ("ESPECIAL", "Régimen Especial"),
    ]

    # Información básica
    nit = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\d{9,11}-\d{1}$", message="Formato NIT: 123456789-0"
            )
        ],
        verbose_name="NIT",
        help_text="Número de Identificación Tributaria con dígito de verificación",
    )

    razon_social = models.CharField(max_length=200, verbose_name="Razón Social")

    nombre_comercial = models.CharField(
        max_length=200, blank=True, verbose_name="Nombre Comercial"
    )

    tipo_empresa = models.CharField(
        max_length=20,
        choices=TIPO_EMPRESA_CHOICES,
        default="SAS",
        verbose_name="Tipo de Empresa",
    )

    # Información tributaria
    regimen_tributario = models.CharField(
        max_length=15,
        choices=REGIMEN_CHOICES,
        default="COMUN",
        verbose_name="Régimen Tributario",
    )

    responsable_iva = models.BooleanField(
        default=True, verbose_name="Responsable de IVA"
    )

    gran_contribuyente = models.BooleanField(
        default=False, verbose_name="Gran Contribuyente"
    )

    autorretenedor = models.BooleanField(default=False, verbose_name="Autorretenedor")

    # Información de contacto
    direccion = models.TextField(max_length=300, verbose_name="Dirección")

    ciudad = models.CharField(max_length=100, verbose_name="Ciudad")

    departamento = models.CharField(
        max_length=100, default="Cundinamarca", verbose_name="Departamento"
    )

    telefono = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^\+?57?[0-9]{7,12}$",
                message="Formato: +5713001234567 o 13001234567",
            )
        ],
        verbose_name="Teléfono",
    )

    email = models.EmailField(verbose_name="Email Corporativo")

    sitio_web = models.URLField(blank=True, verbose_name="Sitio Web")

    # Información contable
    moneda_base = models.CharField(
        max_length=3,
        default="COP",
        verbose_name="Moneda Base",
        help_text="Código ISO de la moneda (COP, USD, EUR)",
    )

    periodo_contable = models.CharField(
        max_length=10,
        default="ANUAL",
        choices=[
            ("MENSUAL", "Mensual"),
            ("BIMESTRAL", "Bimestral"),
            ("TRIMESTRAL", "Trimestral"),
            ("SEMESTRAL", "Semestral"),
            ("ANUAL", "Anual"),
        ],
        verbose_name="Período Contable",
    )

    # Configuración del sistema
    activa = models.BooleanField(default=True, verbose_name="Empresa Activa")

    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Última Actualización"
    )

    # Usuario que creó la empresa (propietario)
    propietario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="empresas_propias",
        verbose_name="Propietario",
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["razon_social"]

    def __str__(self):
        return f"{self.razon_social} ({self.nit})"

    @property
    def nit_formateado(self):
        """Retorna el NIT con formato de puntos"""
        if self.nit:
            nit_sin_dv = self.nit.split("-")[0]
            dv = self.nit.split("-")[1]
            # Formatear con puntos: 123.456.789-0
            nit_formateado = (
                f"{nit_sin_dv[:-6]}.{nit_sin_dv[-6:-3]}.{nit_sin_dv[-3:]}-{dv}"
            )
            return nit_formateado
        return self.nit


class PerfilEmpresa(models.Model):
    """
    Modelo para gestionar los roles de usuarios en cada empresa.
    Un usuario puede tener diferentes roles en diferentes empresas.
    """

    ROL_CHOICES = [
        ("admin", "Administrador"),
        ("contador", "Contador"),
        ("operador", "Operador"),
        ("observador", "Observador"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="perfiles",
        verbose_name="Empresa",
    )

    rol = models.CharField(
        max_length=10, choices=ROL_CHOICES, verbose_name="Rol en la Empresa"
    )

    activo = models.BooleanField(default=True, verbose_name="Perfil Activo")

    fecha_asignacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Asignación"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name="Última Actualización"
    )

    # Usuario que asignó este rol
    asignado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="perfiles_asignados",
        verbose_name="Asignado Por",
    )

    class Meta:
        verbose_name = "Perfil de Usuario en Empresa"
        verbose_name_plural = "Perfiles de Usuarios en Empresas"
        unique_together = ["usuario", "empresa"]
        ordering = ["empresa__razon_social", "usuario__username"]

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username} - {self.empresa.razon_social} ({self.get_rol_display()})"

    @property
    def puede_administrar(self):
        """Verifica si el usuario puede administrar la empresa"""
        return self.rol == "admin"

    @property
    def puede_confirmar_documentos(self):
        """Verifica si el usuario puede confirmar documentos contables"""
        return self.rol in ["admin", "contador"]

    @property
    def solo_lectura_reportes(self):
        """Verifica si el usuario solo puede ver reportes básicos"""
        return self.rol == "operador"

    @property
    def es_observador(self):
        """Verifica si el usuario es observador (solo lectura total)"""
        return self.rol == "observador"

    @property
    def puede_crear_documentos(self):
        """Verifica si el usuario puede crear documentos"""
        return self.rol in ["admin", "contador", "operador"]

    @property
    def puede_editar_catalogos(self):
        """Verifica si el usuario puede editar catálogos"""
        return self.rol in ["admin", "contador", "operador"]


class EmpresaActiva(models.Model):
    """
    Modelo para gestionar qué empresa está activa para cada usuario en su sesión.
    Esto permite que un usuario trabaje con una empresa específica a la vez.
    """

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        related_name="empresa_activa_sesion",
    )

    empresa = models.ForeignKey(
        Empresa, on_delete=models.CASCADE, verbose_name="Empresa Activa"
    )

    fecha_seleccion = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de Selección"
    )

    class Meta:
        verbose_name = "Empresa Activa por Usuario"
        verbose_name_plural = "Empresas Activas por Usuario"

    def __str__(self):
        return f"{self.usuario.username} -> {self.empresa.razon_social}"


class HistorialCambios(models.Model):
    """
    Modelo para registrar todas las acciones de los usuarios en el sistema
    (excepto administradores del holding)
    """

    TIPO_ACCION_CHOICES = [
        # Acciones de empresas
        ("empresa_crear", "Empresa creada"),
        ("empresa_editar", "Empresa editada"),
        ("empresa_activar", "Empresa activada"),
        ("empresa_desactivar", "Empresa desactivada"),
        # Acciones de usuarios
        ("usuario_login", "Inicio de sesión"),
        ("usuario_logout", "Cierre de sesión"),
        ("usuario_cambio_empresa", "Cambio de empresa activa"),
        ("usuario_perfil_actualizado", "Perfil actualizado"),
        # Acciones de terceros
        ("tercero_crear", "Tercero creado"),
        ("tercero_editar", "Tercero editado"),
        ("tercero_eliminar", "Tercero eliminado"),
        # Acciones de productos
        ("producto_crear", "Producto creado"),
        ("producto_editar", "Producto editado"),
        ("producto_eliminar", "Producto eliminado"),
        # Acciones de facturación
        ("factura_crear", "Factura creada"),
        ("factura_editar", "Factura editada"),
        ("factura_anular", "Factura anulada"),
        ("factura_pagar", "Factura pagada"),
        # Acciones de tesorería
        ("pago_crear", "Pago registrado"),
        ("pago_editar", "Pago editado"),
        ("pago_anular", "Pago anulado"),
        ("cobro_crear", "Cobro registrado"),
        ("cobro_editar", "Cobro editado"),
        # Acciones de contabilidad
        ("asiento_crear", "Asiento contable creado"),
        ("asiento_editar", "Asiento contable editado"),
        ("asiento_eliminar", "Asiento contable eliminado"),
        # Acciones de reportes
        ("reporte_generar", "Reporte generado"),
        ("reporte_exportar", "Reporte exportado"),
        # Acciones generales
        ("configuracion_cambiar", "Configuración modificada"),
        ("error_sistema", "Error del sistema"),
        ("acceso_denegado", "Acceso denegado"),
    ]

    # Información básica del cambio
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Usuario",
        help_text="Usuario que realizó la acción",
    )

    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Empresa",
        help_text="Empresa en la que se realizó la acción",
    )

    tipo_accion = models.CharField(
        max_length=50, choices=TIPO_ACCION_CHOICES, verbose_name="Tipo de Acción"
    )

    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="Descripción detallada de la acción realizada",
    )

    # Información técnica
    modelo_afectado = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Modelo Afectado",
        help_text="Nombre del modelo que fue modificado",
    )

    objeto_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID del Objeto",
        help_text="ID del objeto que fue modificado",
    )

    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos Anteriores",
        help_text="Estado anterior del objeto (JSON)",
    )

    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Datos Nuevos",
        help_text="Estado nuevo del objeto (JSON)",
    )

    # Información de contexto
    ip_address = models.GenericIPAddressField(
        null=True, blank=True, verbose_name="Dirección IP"
    )

    user_agent = models.TextField(
        blank=True,
        default="",
        verbose_name="User Agent",
        help_text="Información del navegador/dispositivo",
    )

    url_solicitada = models.URLField(
        max_length=500, blank=True, default="", verbose_name="URL Solicitada"
    )

    metodo_http = models.CharField(
        max_length=10,
        blank=True,
        default="",
        verbose_name="Método HTTP",
        help_text="GET, POST, PUT, DELETE, etc.",
    )

    # Información temporal
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora")

    duracion_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración (ms)",
        help_text="Tiempo que tomó procesar la acción",
    )

    # Estado de la acción
    exitosa = models.BooleanField(
        default=True,
        verbose_name="Exitosa",
        help_text="Si la acción se completó exitosamente",
    )

    mensaje_error = models.TextField(
        blank=True,
        default="",
        verbose_name="Mensaje de Error",
        help_text="Mensaje de error si la acción falló",
    )

    class Meta:
        verbose_name = "Historial de Cambio"
        verbose_name_plural = "Historial de Cambios"
        ordering = ["-fecha_hora"]
        indexes = [
            models.Index(fields=["usuario", "-fecha_hora"]),
            models.Index(fields=["empresa", "-fecha_hora"]),
            models.Index(fields=["tipo_accion", "-fecha_hora"]),
            models.Index(fields=["-fecha_hora"]),
        ]

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_accion_display()} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"

    @property
    def rol_usuario(self):
        """Obtiene el rol del usuario en la empresa donde se realizó la acción"""
        if not self.empresa:
            return "Sin empresa"

        try:
            perfil = PerfilEmpresa.objects.get(
                usuario=self.usuario, empresa=self.empresa, activo=True
            )
            return perfil.get_rol_display()
        except PerfilEmpresa.DoesNotExist:
            return "Sin rol"

    @property
    def tiempo_transcurrido(self):
        """Calcula el tiempo transcurrido desde la acción"""
        from django.utils import timezone
        from datetime import timedelta

        ahora = timezone.now()
        diferencia = ahora - self.fecha_hora

        if diferencia.days > 0:
            return f"Hace {diferencia.days} día{'s' if diferencia.days > 1 else ''}"
        elif diferencia.seconds > 3600:
            horas = diferencia.seconds // 3600
            return f"Hace {horas} hora{'s' if horas > 1 else ''}"
        elif diferencia.seconds > 60:
            minutos = diferencia.seconds // 60
            return f"Hace {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            return "Hace unos segundos"

    @property
    def icono_accion(self):
        """Retorna el icono apropiado para el tipo de acción"""
        iconos = {
            "empresa_crear": "🏢",
            "empresa_editar": "✏️",
            "empresa_activar": "✅",
            "empresa_desactivar": "❌",
            "usuario_login": "🔑",
            "usuario_logout": "🚪",
            "usuario_cambio_empresa": "🔄",
            "usuario_perfil_actualizado": "👤",
            "tercero_crear": "👥",
            "tercero_editar": "✏️",
            "tercero_eliminar": "🗑️",
            "producto_crear": "📦",
            "producto_editar": "✏️",
            "producto_eliminar": "🗑️",
            "factura_crear": "📄",
            "factura_editar": "✏️",
            "factura_anular": "❌",
            "factura_pagar": "💰",
            "pago_crear": "💳",
            "pago_editar": "✏️",
            "pago_anular": "❌",
            "cobro_crear": "💰",
            "cobro_editar": "✏️",
            "asiento_crear": "📊",
            "asiento_editar": "✏️",
            "asiento_eliminar": "🗑️",
            "reporte_generar": "📈",
            "reporte_exportar": "📤",
            "configuracion_cambiar": "⚙️",
            "error_sistema": "⚠️",
            "acceso_denegado": "🚫",
        }
        return iconos.get(self.tipo_accion, "📝")

    @classmethod
    def registrar_accion(
        cls,
        usuario,
        tipo_accion,
        descripcion,
        empresa=None,
        modelo_afectado=None,
        objeto_id=None,
        datos_anteriores=None,
        datos_nuevos=None,
        request=None,
        exitosa=True,
        mensaje_error=None,
    ):
        """
        Método de conveniencia para registrar una acción
        """
        # No registrar acciones de administradores del holding
        if hasattr(usuario, "is_superuser") and usuario.is_superuser:
            return None

        # Obtener información del request si está disponible
        ip_address = None
        user_agent = None
        url_solicitada = None
        metodo_http = None

        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")[
                :500
            ]  # Limitar longitud
            url_solicitada = request.build_absolute_uri()[:500]  # Limitar longitud
            metodo_http = request.method

        return cls.objects.create(
            usuario=usuario,
            empresa=empresa,
            tipo_accion=tipo_accion,
            descripcion=descripcion,
            modelo_afectado=modelo_afectado,
            objeto_id=objeto_id,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
            url_solicitada=url_solicitada,
            metodo_http=metodo_http,
            exitosa=exitosa,
            mensaje_error=mensaje_error,
        )

    @staticmethod
    def _get_client_ip(request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
