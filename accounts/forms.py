"""
Formularios para el sistema de cuentas
Incluye registro completo con perfil colombiano
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import PerfilUsuario


class RegistroCompletoForm(UserCreationForm):
    """
    Formulario de registro completo con perfil colombiano
    Incluye todos los campos necesarios para usuarios colombianos
    """
    # Campos básicos del usuario
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Juan Carlos'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Pérez González'
        })
    )
    
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.com'
        })
    )
    
    # Campos del perfil
    tipo_documento = forms.ChoiceField(
        choices=PerfilUsuario.TIPO_DOCUMENTO_CHOICES,
        required=True,
        label="Tipo de Documento",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    numero_documento = forms.CharField(
        max_length=20,
        required=True,
        label="Número de Documento",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234567890',
            'pattern': '[0-9]{6,20}'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=True,
        label="Teléfono Celular",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+573001234567 o 3001234567',
            'pattern': '(\+57)?[0-9]{10,12}'
        })
    )
    
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    genero = forms.ChoiceField(
        choices=PerfilUsuario.GENERO_CHOICES,
        required=False,
        label="Género",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    estado_civil = forms.ChoiceField(
        choices=PerfilUsuario.ESTADO_CIVIL_CHOICES,
        required=False,
        label="Estado Civil",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    # Información de contacto
    direccion = forms.CharField(
        max_length=200,
        required=False,
        label="Dirección",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Calle 123 #45-67'
        })
    )
    
    ciudad = forms.CharField(
        max_length=100,
        required=False,
        label="Ciudad",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bogotá'
        })
    )
    
    departamento = forms.CharField(
        max_length=100,
        initial='Cundinamarca',
        required=False,
        label="Departamento",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cundinamarca'
        })
    )
    
    codigo_postal = forms.CharField(
        max_length=10,
        required=False,
        label="Código Postal",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '110111'
        })
    )
    
    # Información profesional
    profesion = forms.CharField(
        max_length=100,
        required=False,
        label="Profesión",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contador Público'
        })
    )
    
    empresa = forms.CharField(
        max_length=100,
        required=False,
        label="Empresa",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contadores SAS'
        })
    )
    
    cargo = forms.CharField(
        max_length=100,
        required=False,
        label="Cargo",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contador Senior'
        })
    )
    
    # Términos y condiciones
    acepta_terminos = forms.BooleanField(
        required=True,
        label="Acepto los Términos y Condiciones",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    acepta_politica_privacidad = forms.BooleanField(
        required=True,
        label="Acepto la Política de Privacidad",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    recibir_notificaciones = forms.BooleanField(
        required=False,
        initial=True,
        label="Deseo recibir notificaciones por correo",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'password1', 'password2'
        )
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'juan_perez'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets de contraseñas
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def clean_email(self):
        """Validar que el email no esté en uso"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email
    
    def clean_numero_documento(self):
        """Validar que el número de documento no esté en uso"""
        numero_documento = self.cleaned_data.get('numero_documento')
        if PerfilUsuario.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError("Este número de documento ya está registrado.")
        return numero_documento
    
    def clean_fecha_nacimiento(self):
        """Validar edad mínima"""
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            from datetime import date
            today = date.today()
            edad = today.year - fecha_nacimiento.year
            if edad < 18:
                raise forms.ValidationError("Debe ser mayor de 18 años para registrarse.")
        return fecha_nacimiento
    
    def save(self, commit=True):
        """Guardar usuario y crear perfil completo"""
        # Crear usuario
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # Requiere activación por email
        
        if commit:
            user.save()
            
            # Crear o actualizar perfil
            perfil, created = PerfilUsuario.objects.get_or_create(usuario=user)
            
            # Campos del perfil
            campos_perfil = [
                'tipo_documento', 'numero_documento', 'telefono', 'fecha_nacimiento',
                'genero', 'estado_civil', 'direccion', 'ciudad', 'departamento',
                'codigo_postal', 'profesion', 'empresa', 'cargo',
                'acepta_terminos', 'acepta_politica_privacidad', 'recibir_notificaciones'
            ]
            
            for campo in campos_perfil:
                if campo in self.cleaned_data:
                    setattr(perfil, campo, self.cleaned_data[campo])
            
            perfil.save()
        
        return user


class CustomSetPasswordForm(SetPasswordForm):
    """
    Formulario personalizado para cambio de contraseña
    Incluye validación para no permitir la misma contraseña actual
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar widgets
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (mínimo 8 caracteres)'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    
    def clean_new_password1(self):
        """Validar que la nueva contraseña no sea igual a la actual"""
        new_password1 = self.cleaned_data.get('new_password1')
        
        if new_password1:
            # Verificar si la nueva contraseña es igual a la actual
            if self.user.check_password(new_password1):
                raise forms.ValidationError(
                    "❌ La nueva contraseña no puede ser igual a la contraseña actual. "
                    "Por favor, elige una contraseña diferente."
                )
        
        return new_password1
    
    def clean(self):
        """Validaciones adicionales"""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        # Validar que las contraseñas coincidan
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(
                    "❌ Las contraseñas no coinciden. Por favor, verifica que ambas sean iguales."
                )
        
        return cleaned_data
