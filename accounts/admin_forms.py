"""
Formularios personalizados para el admin de Django
Simplifica la creación de usuarios con perfil integrado
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario
from django.db import transaction

# Texto de ayuda reutilizable
IS_ACTIVE_HELP = "Determina si el usuario puede iniciar sesión"


class UsuarioCompletoAdminForm(UserCreationForm):
    """
    Formulario unificado para crear usuarios con perfil desde el admin
    Combina User + PerfilUsuario en un solo formulario
    """
    
    # Campos básicos del usuario (Django User)
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label="Nombres",
        help_text="Nombres completos del usuario"
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label="Apellidos", 
        help_text="Apellidos completos del usuario"
    )
    
    email = forms.EmailField(
        required=True,
        label="Correo Electrónico",
        help_text="Email único para el usuario"
    )
    
    # Campos del perfil (PerfilUsuario) - Los más importantes
    tipo_documento = forms.ChoiceField(
        choices=PerfilUsuario.TIPO_DOCUMENTO_CHOICES,
        required=True,
        label="Tipo de Documento",
        help_text="Tipo de identificación"
    )
    
    numero_documento = forms.CharField(
        max_length=20,
        required=True,
        label="Número de Documento",
        help_text="Número de identificación único (sin puntos ni espacios)"
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=True,
        label="Teléfono",
        help_text="Número de teléfono celular (ej: +573001234567)"
    )
    
    fecha_nacimiento = forms.DateField(
        required=False,
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Fecha de nacimiento (opcional)"
    )
    
    genero = forms.ChoiceField(
        choices=[('', '-- Seleccionar --')] + PerfilUsuario.GENERO_CHOICES,
        required=False,
        label="Género",
        help_text="Género del usuario (opcional)"
    )
    
    # Información de contacto
    ciudad = forms.CharField(
        max_length=100,
        required=False,
        label="Ciudad",
        help_text="Ciudad de residencia"
    )
    
    departamento = forms.CharField(
        max_length=100,
        initial='Cundinamarca',
        required=False,
        label="Departamento",
        help_text="Departamento de residencia"
    )
    
    # Información profesional
    profesion = forms.CharField(
        max_length=100,
        required=False,
        label="Profesión",
        help_text="Profesión u ocupación"
    )
    
    # Configuración del sistema
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        label="Usuario Activo",
        help_text=IS_ACTIVE_HELP
    )
    
    is_staff = forms.BooleanField(
        initial=False,
        required=False,
        label="Es Staff",
        help_text="Permite acceso al admin de Django"
    )
    
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'is_active', 'is_staff'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mejorar help texts
        self.fields['username'].help_text = "Nombre de usuario único para iniciar sesión"
        self.fields['password1'].help_text = "Contraseña segura (mínimo 8 caracteres)"
        self.fields['password2'].help_text = "Confirmar la contraseña"
        
        # Hacer campos más intuitivos
        self.fields['username'].label = "Nombre de Usuario"
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Confirmar Contraseña"
    
    def clean_email(self):
        """Validar que el email sea único"""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    def clean_numero_documento(self):
        """Validar que el número de documento sea único"""
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento and PerfilUsuario.objects.filter(numero_documento=numero_documento).exists():
            raise forms.ValidationError("Este número de documento ya está registrado.")
        return numero_documento
    
    def clean_telefono(self):
        """Validar formato del teléfono"""
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Limpiar el teléfono de espacios y caracteres especiales
            telefono_limpio = ''.join(filter(str.isdigit, telefono.replace('+', '')))
            
            # Validar longitud
            if len(telefono_limpio) < 10 or len(telefono_limpio) > 12:
                raise forms.ValidationError("El teléfono debe tener entre 10 y 12 dígitos.")
            
            # Si no tiene código de país, asumir Colombia (+57)
            if len(telefono_limpio) == 10:
                telefono = f"+57{telefono_limpio}"
            elif len(telefono_limpio) == 12 and telefono_limpio.startswith('57'):
                telefono = f"+{telefono_limpio}"
            else:
                telefono = f"+{telefono_limpio}"
        
        return telefono
    
    @transaction.atomic
    def save(self, commit=True):
        """Guardar usuario y crear perfil automáticamente"""
        # Crear el usuario
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = self.cleaned_data.get('is_active', True)
        user.is_staff = self.cleaned_data.get('is_staff', False)
        
        if commit:
            user.save()
            
            # Crear o actualizar el perfil automáticamente
            perfil, created = PerfilUsuario.objects.get_or_create(
                usuario=user,
                defaults={
                    'tipo_documento': self.cleaned_data.get('tipo_documento', 'CC'),
                    'numero_documento': self.cleaned_data.get('numero_documento', ''),
                    'telefono': self.cleaned_data.get('telefono', ''),
                    'fecha_nacimiento': self.cleaned_data.get('fecha_nacimiento'),
                    'genero': self.cleaned_data.get('genero', ''),
                    'ciudad': self.cleaned_data.get('ciudad', ''),
                    'departamento': self.cleaned_data.get('departamento', 'Cundinamarca'),
                    'profesion': self.cleaned_data.get('profesion', ''),
                    'acepta_terminos': True,  # Por defecto True en admin
                    'acepta_politica_privacidad': True,  # Por defecto True en admin
                }
            )
            
            # Si el perfil ya existía, actualizarlo
            if not created:
                for campo, valor in {
                    'tipo_documento': self.cleaned_data.get('tipo_documento'),
                    'numero_documento': self.cleaned_data.get('numero_documento'),
                    'telefono': self.cleaned_data.get('telefono'),
                    'fecha_nacimiento': self.cleaned_data.get('fecha_nacimiento'),
                    'genero': self.cleaned_data.get('genero'),
                    'ciudad': self.cleaned_data.get('ciudad'),
                    'departamento': self.cleaned_data.get('departamento'),
                    'profesion': self.cleaned_data.get('profesion'),
                }.items():
                    if valor is not None and valor != '':
                        setattr(perfil, campo, valor)
                
                perfil.save()
        
        return user


class PerfilUsuarioEditForm(forms.ModelForm):
    """
    Formulario simplificado para editar solo el perfil
    Usado en el inline del admin
    """
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'tipo_documento', 'numero_documento', 'telefono', 'fecha_nacimiento',
            'genero', 'estado_civil', 'direccion', 'ciudad', 'departamento',
            'codigo_postal', 'profesion', 'empresa', 'cargo', 'activo'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer campos opcionales más claros
        for field_name, field in self.fields.items():
            if not field.required:
                field.help_text = f"{field.help_text or ''} (Opcional)".strip()


class PerfilUsuarioCompletoForm(forms.ModelForm):
    """
    Formulario inteligente para crear PerfilUsuario con opción de crear Usuario automáticamente
    """
    
    # Opción para crear usuario automáticamente
    crear_usuario_automaticamente = forms.BooleanField(
        required=False,
        initial=True,
        label="✨ Crear usuario automáticamente",
        help_text="Si está marcado, se creará un usuario nuevo con los datos proporcionados"
    )
    
    # Campos para crear usuario nuevo (solo si crear_usuario_automaticamente está marcado)
    username = forms.CharField(
        max_length=150,
        required=False,
        label="Nombre de Usuario",
        help_text="Nombre único para iniciar sesión (se generará automáticamente si se deja vacío)"
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Nombres",
        help_text="Nombres completos del usuario"
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Apellidos", 
        help_text="Apellidos completos del usuario"
    )
    
    email = forms.EmailField(
        required=False,
        label="Correo Electrónico",
        help_text="Email único para el usuario (se generará automáticamente si se deja vacío)"
    )
    
    password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(),
        label="Contraseña",
        help_text="Contraseña para el usuario (se generará automáticamente si se deja vacía)"
    )
    
    is_active = forms.BooleanField(
        initial=True,
        required=False,
        label="Usuario Activo",
        help_text="Determina si el usuario puede iniciar sesión"
    )
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'usuario', 'tipo_documento', 'numero_documento', 'telefono', 
            'fecha_nacimiento', 'genero', 'estado_civil', 'direccion', 
            'ciudad', 'departamento', 'codigo_postal', 'profesion', 
            'empresa', 'cargo', 'activo'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer el campo usuario no requerido inicialmente
        self.fields['usuario'].required = False
        self.fields['usuario'].help_text = "Seleccionar usuario existente o dejar vacío para crear uno nuevo"
        
        # Hacer campos opcionales más claros
        for field_name, field in self.fields.items():
            if not field.required and field_name not in ['crear_usuario_automaticamente', 'usuario']:
                field.help_text = f"{field.help_text or ''} (Opcional)".strip()
    
    def clean(self):
        cleaned_data = super().clean()
        crear_automatico = cleaned_data.get('crear_usuario_automaticamente')
        usuario_existente = cleaned_data.get('usuario')
        
        self._validate_user_selection(crear_automatico, usuario_existente)
        
        if crear_automatico:
            self._validate_min_fields(cleaned_data)
            self._ensure_generated_defaults(cleaned_data)
        
        return cleaned_data

    # === Helpers para reducir complejidad cognitiva ===
    def _validate_user_selection(self, crear_automatico, usuario_existente):
        """Valida que haya selección de usuario o activación de creación automática"""
        if not crear_automatico and not usuario_existente:
            raise forms.ValidationError(
                "Debe seleccionar un usuario existente o marcar 'Crear usuario automáticamente'"
            )

    def _validate_min_fields(self, cleaned_data):
        """Valida campos mínimos requeridos para crear usuario automático"""
        if not cleaned_data.get('numero_documento'):
            raise forms.ValidationError("El número de documento es requerido para crear el usuario")
        if not cleaned_data.get('telefono'):
            raise forms.ValidationError("El teléfono es requerido para crear el usuario")

    def _ensure_generated_defaults(self, cleaned_data):
        """Genera valores por defecto cuando faltan datos para la creación automática"""
        numero_documento = cleaned_data.get('numero_documento')
        if not cleaned_data.get('first_name'):
            cleaned_data['first_name'] = f"Usuario {numero_documento}"
        if not cleaned_data.get('last_name'):
            cleaned_data['last_name'] = "Generado"
        if not cleaned_data.get('username'):
            base_username = f"user_{numero_documento}"
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            cleaned_data['username'] = username
        if not cleaned_data.get('email'):
            cleaned_data['email'] = f"{cleaned_data['username']}@temp.local"
        if not cleaned_data.get('password'):
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits
            cleaned_data['password'] = ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def clean_numero_documento(self):
        """Validar que el número de documento sea único"""
        numero_documento = self.cleaned_data.get('numero_documento')
        if numero_documento:
            # Excluir el perfil actual si estamos editando
            existing_profiles = PerfilUsuario.objects.filter(numero_documento=numero_documento)
            if self.instance and self.instance.pk:
                existing_profiles = existing_profiles.exclude(pk=self.instance.pk)
            
            if existing_profiles.exists():
                raise forms.ValidationError("Este número de documento ya está registrado.")
        return numero_documento
    
    def clean_email(self):
        """Validar que el email sea único si se va a crear usuario"""
        email = self.cleaned_data.get('email')
        crear_automatico = self.cleaned_data.get('crear_usuario_automaticamente')
        
        if email and crear_automatico:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email
    
    def clean_username(self):
        """Validar que el username sea único si se va a crear usuario"""
        username = self.cleaned_data.get('username')
        crear_automatico = self.cleaned_data.get('crear_usuario_automaticamente')
        
        if username and crear_automatico:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("Este nombre de usuario ya está registrado.")
        return username
    
    @transaction.atomic
    def save(self, commit=True):
        """Guardar perfil y crear usuario si es necesario"""
        crear_automatico = self.cleaned_data.get('crear_usuario_automaticamente')
        
        if crear_automatico:
            # Crear usuario automáticamente
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                is_active=self.cleaned_data.get('is_active', True)
            )
            
            # IMPORTANTE: La señal post_save ya creó un PerfilUsuario para este usuario
            # Obtener el perfil existente en lugar de crear uno nuevo
            try:
                perfil = PerfilUsuario.objects.get(usuario=user)
                
                # Actualizar con cleaned_data directamente
                perfil.tipo_documento = self.cleaned_data.get('tipo_documento', perfil.tipo_documento)
                perfil.numero_documento = self.cleaned_data.get('numero_documento', perfil.numero_documento)
                perfil.telefono = self.cleaned_data.get('telefono', perfil.telefono)
                perfil.fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
                perfil.genero = self.cleaned_data.get('genero', '')
                perfil.estado_civil = self.cleaned_data.get('estado_civil', '')
                perfil.direccion = self.cleaned_data.get('direccion', '')
                perfil.ciudad = self.cleaned_data.get('ciudad', '')
                perfil.departamento = self.cleaned_data.get('departamento', 'Cundinamarca')
                perfil.codigo_postal = self.cleaned_data.get('codigo_postal', '')
                perfil.profesion = self.cleaned_data.get('profesion', '')
                perfil.empresa = self.cleaned_data.get('empresa', '')
                perfil.cargo = self.cleaned_data.get('cargo', '')
                perfil.activo = self.cleaned_data.get('activo', True)
                
                # IMPORTANTE: Asignar el perfil actualizado a self.instance
                # para que Django Admin lo reconozca como el objeto guardado
                self.instance = perfil
                
                if commit:
                    perfil.save()
                
                return perfil
                
            except PerfilUsuario.DoesNotExist:
                # Si por alguna razón no se creó el perfil (señal deshabilitada), asignar usuario
                self.instance.usuario = user
        
        # Guardar el perfil (para caso de usuario existente o perfil no creado por señal)
        perfil = super().save(commit=commit)
        
        return perfil
    
    def save_m2m(self):
        """
        Método requerido por Django Admin para guardar relaciones many-to-many.
        PerfilUsuario no tiene campos M2M, pero Django Admin espera este método.
        """
        # Como no hay campos many-to-many en PerfilUsuario, este método no hace nada
        # pero debe existir para evitar AttributeError en Django Admin
        pass


class UsuarioEditForm(forms.ModelForm):
    """
    Formulario para editar usuarios existentes
    Incluye campos básicos del User
    """
    
    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'is_superuser'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Mejorar labels y help texts
        self.fields['username'].help_text = "Nombre de usuario único (no se puede cambiar fácilmente)"
        self.fields['first_name'].label = "Nombres"
        self.fields['last_name'].label = "Apellidos"
        self.fields['email'].help_text = "Correo electrónico único"
        self.fields['is_active'].help_text = IS_ACTIVE_HELP
        self.fields['is_staff'].help_text = "Permite acceso al admin de Django"
        self.fields['is_superuser'].help_text = "Otorga todos los permisos (usar con precaución)"
    
    def clean_email(self):
        """Validar email único excluyendo el usuario actual"""
        email = self.cleaned_data.get('email')
        if email:
            # Excluir el usuario actual de la validación
            existing_users = User.objects.filter(email=email)
            if self.instance:
                existing_users = existing_users.exclude(pk=self.instance.pk)
            
            if existing_users.exists():
                raise forms.ValidationError("Este correo electrónico ya está registrado por otro usuario.")
        
        return email
