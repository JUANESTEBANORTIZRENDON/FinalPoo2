"""
Serializers para API REST con JWT
Maneja registro completo, activación y reset de clave de acceso
Sistema en español para Colombia
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from accounts.models import PerfilUsuario


class RegistroCompletoSerializer(serializers.ModelSerializer):
    """
    Serializer para registro completo de usuarios colombianos
    Incluye información personal, contacto y profesional
    """
    # Campos del usuario base
    password1 = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Clave de acceso (mínimo 8 caracteres)"
    )
    password2 = serializers.CharField(
        write_only=True,
        help_text="Confirmar clave de acceso"
    )
    
    # Campos del perfil extendido
    tipo_documento = serializers.ChoiceField(
        choices=PerfilUsuario.TIPO_DOCUMENTO_CHOICES,
        default='CC',
        help_text="Tipo de documento de identidad"
    )
    numero_documento = serializers.CharField(
        max_length=20,
        help_text="Número de documento sin puntos ni espacios"
    )
    telefono = serializers.CharField(
        max_length=15,
        help_text="Número celular: +573001234567 o 3001234567"
    )
    fecha_nacimiento = serializers.DateField(
        required=False,
        help_text="Fecha de nacimiento (YYYY-MM-DD)"
    )
    genero = serializers.ChoiceField(
        choices=PerfilUsuario.GENERO_CHOICES,
        required=False,
        help_text="Género"
    )
    estado_civil = serializers.ChoiceField(
        choices=PerfilUsuario.ESTADO_CIVIL_CHOICES,
        required=False,
        help_text="Estado civil"
    )
    
    # Información de contacto
    direccion = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Dirección completa de residencia"
    )
    ciudad = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Ciudad de residencia"
    )
    departamento = serializers.CharField(
        max_length=100,
        default='Cundinamarca',
        help_text="Departamento"
    )
    codigo_postal = serializers.CharField(
        max_length=10,
        required=False,
        help_text="Código postal"
    )
    
    # Información profesional
    profesion = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Profesión u ocupación"
    )
    empresa = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Empresa donde trabaja"
    )
    cargo = serializers.CharField(
        max_length=100,
        required=False,
        help_text="Cargo o posición"
    )
    
    # Términos y condiciones
    acepta_terminos = serializers.BooleanField(
        help_text="Debe aceptar los términos y condiciones"
    )
    acepta_politica_privacidad = serializers.BooleanField(
        help_text="Debe aceptar la política de privacidad"
    )
    recibir_notificaciones = serializers.BooleanField(
        default=True,
        help_text="Recibir notificaciones por email"
    )
    
    class Meta:
        model = User
        fields = (
            # Campos básicos del usuario
            'username', 'email', 'password1', 'password2', 'first_name', 'last_name',
            # Campos del perfil
            'tipo_documento', 'numero_documento', 'telefono', 'fecha_nacimiento',
            'genero', 'estado_civil', 'direccion', 'ciudad', 'departamento', 
            'codigo_postal', 'profesion', 'empresa', 'cargo',
            'acepta_terminos', 'acepta_politica_privacidad', 'recibir_notificaciones'
        )
        extra_kwargs = {
            'email': {'required': True, 'help_text': 'Email válido requerido'},
            'username': {'help_text': 'Nombre de usuario único'},
            'first_name': {'required': True, 'help_text': 'Nombres completos'},
            'last_name': {'required': True, 'help_text': 'Apellidos completos'},
        }
    
    def validate_email(self, value):
        """Validar que el email no esté en uso"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_numero_documento(self, value):
        """Validar que el número de documento no esté en uso"""
        if PerfilUsuario.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Este número de documento ya está registrado.")
        return value
    
    def validate_acepta_terminos(self, value):
        """Validar que acepta términos y condiciones"""
        if not value:
            raise serializers.ValidationError("Debe aceptar los términos y condiciones.")
        return value
    
    def validate_acepta_politica_privacidad(self, value):
        """Validar que acepta política de privacidad"""
        if not value:
            raise serializers.ValidationError("Debe aceptar la política de privacidad.")
        return value
    
    def validate(self, attrs):
        """Validaciones generales"""
        # Validar claves de acceso
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': 'Las claves de acceso no coinciden.'
            })
        
        # Validar fortaleza de clave de acceso
        try:
            validate_password(attrs['password1'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'password1': list(e.messages)
            })
        
        # Validar edad mínima (si se proporciona fecha de nacimiento)
        if attrs.get('fecha_nacimiento'):
            from datetime import date
            today = date.today()
            edad = today.year - attrs['fecha_nacimiento'].year
            if edad < 18:
                raise serializers.ValidationError({
                    'fecha_nacimiento': 'Debe ser mayor de 18 años para registrarse.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Crear usuario completo con perfil extendido"""
        # Separar campos del usuario y del perfil
        perfil_data = {}
        campos_perfil = [
            'tipo_documento', 'numero_documento', 'telefono', 'fecha_nacimiento',
            'genero', 'estado_civil', 'direccion', 'ciudad', 'departamento',
            'codigo_postal', 'profesion', 'empresa', 'cargo',
            'acepta_terminos', 'acepta_politica_privacidad', 'recibir_notificaciones'
        ]
        
        for campo in campos_perfil:
            if campo in validated_data:
                perfil_data[campo] = validated_data.pop(campo)
        
        # Remover campos de confirmación
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        
        # Crear usuario inactivo (requiere activación por email)
        user = User.objects.create_user(
            password=password,
            is_active=False,  # Requiere activación
            **validated_data
        )
        
        # Actualizar el perfil creado automáticamente por la señal
        if hasattr(user, 'perfil'):
            for campo, valor in perfil_data.items():
                setattr(user.perfil, campo, valor)
            user.perfil.save()
        
        return user


# Mantener el serializer simple para compatibilidad
class RegistroSerializer(RegistroCompletoSerializer):
    """
    Serializer simplificado para registro básico
    Mantiene compatibilidad con versiones anteriores
    """
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password1', 'password2', 'first_name', 'last_name',
            'tipo_documento', 'numero_documento', 'telefono',
            'acepta_terminos', 'acepta_politica_privacidad'
        )
        extra_kwargs = {
            'email': {'required': True, 'help_text': 'Email válido requerido'},
            'username': {'help_text': 'Nombre de usuario único'},
            'first_name': {'required': True, 'help_text': 'Nombres completos'},
            'last_name': {'required': True, 'help_text': 'Apellidos completos'},
        }


class MeSerializer(serializers.ModelSerializer):
    """
    Serializer para información completa del usuario autenticado
    Incluye datos del perfil extendido
    """
    nombre_completo = serializers.SerializerMethodField()
    esta_verificado = serializers.SerializerMethodField()
    
    # Campos del perfil
    tipo_documento = serializers.CharField(source='perfil.tipo_documento', read_only=True)
    numero_documento = serializers.CharField(source='perfil.numero_documento', read_only=True)
    documento_completo = serializers.CharField(source='perfil.documento_completo', read_only=True)
    telefono = serializers.CharField(source='perfil.telefono', read_only=True)
    fecha_nacimiento = serializers.DateField(source='perfil.fecha_nacimiento', read_only=True)
    edad = serializers.IntegerField(source='perfil.edad', read_only=True)
    genero = serializers.CharField(source='perfil.get_genero_display', read_only=True)
    estado_civil = serializers.CharField(source='perfil.get_estado_civil_display', read_only=True)
    
    # Información de contacto
    direccion = serializers.CharField(source='perfil.direccion', read_only=True)
    ciudad = serializers.CharField(source='perfil.ciudad', read_only=True)
    departamento = serializers.CharField(source='perfil.departamento', read_only=True)
    pais = serializers.CharField(source='perfil.pais', read_only=True)
    
    # Información profesional
    profesion = serializers.CharField(source='perfil.profesion', read_only=True)
    empresa = serializers.CharField(source='perfil.empresa', read_only=True)
    cargo = serializers.CharField(source='perfil.cargo', read_only=True)
    
    class Meta:
        model = User
        fields = (
            # Información básica
            'id', 'username', 'email', 'first_name', 'last_name', 
            'nombre_completo', 'esta_verificado', 'date_joined', 'last_login',
            # Información del perfil
            'tipo_documento', 'numero_documento', 'documento_completo', 'telefono',
            'fecha_nacimiento', 'edad', 'genero', 'estado_civil',
            'direccion', 'ciudad', 'departamento', 'pais',
            'profesion', 'empresa', 'cargo'
        )
        read_only_fields = ('id', 'username', 'date_joined', 'last_login')
    
    def get_nombre_completo(self, obj):
        """Retorna nombre completo del usuario"""
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username
    
    def get_esta_verificado(self, obj):
        """Retorna si el usuario está verificado (activo)"""
        return obj.is_active


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer para solicitar reset de clave de acceso
    Solo requiere email
    """
    email = serializers.EmailField(
        help_text="Email del usuario para enviar enlace de recuperación"
    )
    
    def validate_email(self, value):
        """Validar que el email exista en el sistema"""
        if not User.objects.filter(email=value, is_active=True).exists():
            # Por seguridad, no revelamos si el email existe o no
            # Pero internamente validamos
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer para confirmar reset de clave de acceso con token
    """
    token = serializers.CharField(
        help_text="Token de recuperación recibido por email"
    )
    password1 = serializers.CharField(
        min_length=8,
        help_text="Nueva clave de acceso (mínimo 8 caracteres)"
    )
    password2 = serializers.CharField(
        help_text="Confirmar nueva clave de acceso"
    )
    
    def validate(self, attrs):
        """Validar que las claves de acceso coincidan"""
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': 'Las claves de acceso no coinciden.'
            })
        
        # Validar fortaleza de clave de acceso
        try:
            validate_password(attrs['password1'])
        except ValidationError as e:
            raise serializers.ValidationError({
                'password1': list(e.messages)
            })
        
        return attrs


class ActivarCuentaSerializer(serializers.Serializer):
    """
    Serializer para activar cuenta con token de email
    """
    token = serializers.CharField(
        help_text="Token de activación recibido por email"
    )
    
    def validate_token(self, value):
        """Validar formato del token"""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Token inválido.")
        return value
