# 📊 S_CONTABLE - DOCUMENTACIÓN COMPLETA

## 🎯 **DESCRIPCIÓN DEL PROYECTO**

S_CONTABLE es un **Sistema Contable Colombiano** desarrollado en Django que combina:
- **Sistema Web Tradicional** (MVT con sesiones)
- **API REST** (JWT para móviles y sistemas externos)
- **Perfiles de Usuario Colombianos** (documentos, teléfonos, ubicaciones)
- **Autenticación Dual** (sesiones web + tokens JWT)

---

## 🏗️ **ARQUITECTURA DEL SISTEMA**

### **🔧 TECNOLOGÍAS PRINCIPALES:**
- **Backend**: Django 5.2.7 + Django REST Framework
- **Base de Datos**: PostgreSQL (Neon Cloud)
- **Autenticación**: Django Sessions + JWT (SimpleJWT)
- **Email**: Gmail SMTP con contraseñas de aplicación
- **Frontend**: Bootstrap 5 + JavaScript
- **Internacionalización**: Español Colombiano (es-co)

### **🌐 ARQUITECTURA DUAL:**

#### **Sistema MVT (Web Tradicional):**
```
Usuario → Navegador → Django Views → Templates HTML → Sesiones Cookie
```
- **Login**: `/accounts/login/`
- **Dashboard**: `/accounts/dashboard/`
- **Admin**: `/admin/`
- **Autenticación**: Sesiones Django tradicionales

#### **Sistema API REST (Móviles/Externos):**
```
App/Sistema → HTTP Request → Django API → JSON Response → JWT Tokens
```
- **Login**: `/api/token/`
- **Datos**: `/api/me/`
- **Registro**: `/api/registro-completo/`
- **Autenticación**: Bearer Tokens JWT

---

## 📁 **ESTRUCTURA DE DIRECTORIOS**

```
S_CONTABLE/
├── 📁 core/                          # Configuración principal
│   ├── settings.py                   # Configuración Django
│   ├── urls.py                       # URLs principales
│   └── wsgi.py                       # WSGI para producción
│
├── 📁 accounts/                      # Sistema de usuarios
│   ├── 📁 migrations/                # Migraciones de BD
│   ├── 📁 templates/accounts/        # Templates HTML
│   │   ├── base.html                 # Template base
│   │   ├── login.html                # Página de login
│   │   ├── register.html             # Registro de usuarios
│   │   ├── dashboard.html            # Dashboard principal
│   │   └── password_reset_*.html     # Reset de contraseña
│   ├── models.py                     # Modelo PerfilUsuario
│   ├── views.py                      # Vistas web + API
│   ├── forms.py                      # Formularios Django
│   ├── admin.py                      # Panel administrativo
│   ├── urls.py                       # URLs de accounts
│   └── admin_views.py                # Vistas admin personalizadas
│
├── 📁 api/                           # API REST
│   ├── views.py                      # Vistas API (JWT)
│   ├── serializers.py                # Serializadores DRF
│   └── urls.py                       # URLs de API
│
├── 📁 templates/                     # Templates globales
│   └── 📁 admin/                     # Templates admin personalizados
│
├── 📁 static/                        # Archivos estáticos
│   ├── 📁 css/                       # Estilos CSS
│   ├── 📁 js/                        # JavaScript
│   └── 📁 images/                    # Imágenes
│
├── 📁 env/                           # Entorno virtual Python
├── 📁 scripts/                       # Scripts de utilidad
├── .env                              # Variables de entorno
├── requirements.txt                  # Dependencias Python
├── manage.py                         # Comando Django
└── 📄 DOCUMENTACION_*.md             # Documentación
```

---

## 👤 **SISTEMA DE USUARIOS COLOMBIANOS**

### **🆔 MODELO PerfilUsuario:**

#### **Información Personal:**
- **Documento**: CC, CE, TI, PP, NIT (validación colombiana)
- **Nombres y Apellidos**: Campos separados
- **Fecha de Nacimiento**: Validación +18 años
- **Género**: Masculino, Femenino, Otro, Prefiero no decir
- **Estado Civil**: Soltero, Casado, Unión libre, etc.

#### **Información de Contacto:**
- **Teléfono**: Validación formato colombiano (+57)
- **Email**: Único en el sistema
- **Dirección Completa**: Calle, ciudad, departamento
- **Código Postal**: Formato colombiano

#### **Información Profesional:**
- **Profesión**: Campo libre
- **Empresa**: Lugar de trabajo
- **Cargo**: Posición actual

#### **Configuraciones:**
- **Términos y Condiciones**: Obligatorio
- **Política de Privacidad**: Obligatorio
- **Notificaciones**: Opcional

### **🔐 AUTENTICACIÓN DUAL:**

#### **Web Tradicional (Sesiones):**
- **Login**: Formulario HTML → Cookie de sesión
- **Logout**: Elimina sesión del servidor
- **Persistencia**: Sesión en base de datos
- **Seguridad**: CSRF tokens, secure cookies

#### **API REST (JWT):**
- **Login**: JSON → Access Token (15 min) + Refresh Token (1 día)
- **Logout**: Blacklist de tokens
- **Persistencia**: Token en cliente (app móvil)
- **Seguridad**: Firma digital, expiración automática

---

## 🔧 **FUNCIONALIDADES PRINCIPALES**

### **👥 GESTIÓN DE USUARIOS:**

#### **Registro Completo:**
- ✅ Formulario con 20+ campos colombianos
- ✅ Validaciones específicas (documento, teléfono)
- ✅ Email de activación obligatorio
- ✅ Creación automática de perfil

#### **Autenticación:**
- ✅ Login web tradicional
- ✅ Login API con JWT
- ✅ Reset de contraseña por email
- ✅ Validación de contraseña (no igual a actual)

#### **Panel Administrativo:**
- ✅ Vista personalizada de usuarios
- ✅ Filtros por documento, ciudad, departamento
- ✅ Eliminación segura con validaciones
- ✅ Información completa del perfil

### **📧 SISTEMA DE EMAILS:**

#### **Configuración Gmail SMTP:**
- ✅ Emails en español colombiano
- ✅ Templates personalizados con emojis
- ✅ Información del perfil en emails
- ✅ Contraseñas de aplicación seguras

#### **Tipos de Email:**
- **Activación de cuenta**: Registro nuevo usuario
- **Reset de contraseña**: Recuperación de acceso
- **Notificaciones**: Cambios importantes

### **🌐 API REST COMPLETA:**

#### **Endpoints de Autenticación:**
- `POST /api/token/` - Obtener tokens JWT
- `POST /api/token/refresh/` - Renovar access token
- `POST /api/logout/` - Cerrar sesión (blacklist)
- `GET /api/me/` - Datos del usuario autenticado

#### **Endpoints de Usuario:**
- `POST /api/registro/` - Registro básico
- `POST /api/registro-completo/` - Registro con perfil colombiano
- `POST /api/activar/` - Activar cuenta por email
- `POST /api/password/reset/` - Solicitar reset contraseña
- `POST /api/password/reset/confirm/` - Confirmar reset

### **🛡️ SEGURIDAD IMPLEMENTADA:**

#### **Validaciones de Entrada:**
- ✅ Documento único (6-20 dígitos)
- ✅ Email único en el sistema
- ✅ Teléfono formato colombiano
- ✅ Contraseñas seguras (8+ caracteres)
- ✅ Edad mínima 18 años

#### **Protección de Datos:**
- ✅ CSRF protection en formularios
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection en templates
- ✅ Secure cookies en producción
- ✅ JWT con firma digital

#### **Control de Acceso:**
- ✅ Usuarios inactivos no pueden acceder
- ✅ Tokens JWT con expiración
- ✅ Blacklist de tokens en logout
- ✅ Validación de permisos en admin

---

## 🗄️ **BASE DE DATOS**

### **📊 MODELOS PRINCIPALES:**

#### **User (Django built-in):**
```python
- username: CharField (único)
- email: EmailField (único)
- first_name: CharField
- last_name: CharField
- is_active: BooleanField
- is_staff: BooleanField
- date_joined: DateTimeField
```

#### **PerfilUsuario (Personalizado):**
```python
- usuario: OneToOneField(User)
- tipo_documento: CharField (CC, CE, TI, PP, NIT)
- numero_documento: CharField (único)
- telefono: CharField
- fecha_nacimiento: DateField
- genero: CharField
- estado_civil: CharField
- direccion: CharField
- ciudad: CharField
- departamento: CharField
- codigo_postal: CharField
- profesion: CharField
- empresa: CharField
- cargo: CharField
- acepta_terminos: BooleanField
- acepta_politica_privacidad: BooleanField
- recibir_notificaciones: BooleanField
- fecha_creacion: DateTimeField
- fecha_actualizacion: DateTimeField
```

### **🔗 RELACIONES:**
- **User ↔ PerfilUsuario**: Relación 1:1 (automática vía signals)
- **Eliminación en cascada**: Al eliminar User se elimina PerfilUsuario
- **Integridad referencial**: Validaciones en base de datos

---

## 🌍 **CONFIGURACIÓN REGIONAL**

### **🇨🇴 LOCALIZACIÓN COLOMBIANA:**
- **Idioma**: Español de Colombia (es-co)
- **Zona Horaria**: America/Bogota (UTC-5)
- **Formato Fecha**: DD/MM/YYYY
- **Moneda**: Peso Colombiano (COP)

### **📱 VALIDACIONES ESPECÍFICAS:**
- **Documentos**: Formatos oficiales colombianos
- **Teléfonos**: +57 o formato nacional (10 dígitos)
- **Ciudades**: Principales ciudades colombianas
- **Departamentos**: 32 departamentos + Bogotá D.C.

---

## 🔧 **CONFIGURACIÓN DE DESARROLLO**

### **📋 VARIABLES DE ENTORNO (.env):**
```env
# Django
DEBUG=True
SECRET_KEY=tu-secret-key-super-segura

# Base de Datos
DATABASE_URL=postgresql://user:pass@host:port/db

# Email
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=contraseña-de-aplicacion-16-chars

# Seguridad
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

### **🐍 DEPENDENCIAS PRINCIPALES:**
```
Django==5.2.7
djangorestframework==3.15.2
djangorestframework-simplejwt==5.3.0
psycopg2-binary==2.9.9
python-dotenv==1.0.1
dj-database-url==2.2.0
```

---

## 🚀 **DESPLIEGUE Y PRODUCCIÓN**

### **☁️ SERVICIOS CLOUD:**
- **Base de Datos**: Neon PostgreSQL
- **Email**: Gmail SMTP
- **Hosting**: Compatible con Heroku, Railway, DigitalOcean
- **Archivos Estáticos**: Configurado para WhiteNoise

### **🔒 CONFIGURACIÓN DE PRODUCCIÓN:**
- **DEBUG=False**: Desactivar modo debug
- **ALLOWED_HOSTS**: Dominios permitidos
- **SECURE_SSL_REDIRECT**: Forzar HTTPS
- **CSRF_COOKIE_SECURE**: Cookies seguras
- **SESSION_COOKIE_SECURE**: Sesiones seguras

---

## 📈 **ESCALABILIDAD Y FUTURO**

### **🔮 CARACTERÍSTICAS PREPARADAS:**
- ✅ **API REST**: Lista para apps móviles
- ✅ **JWT Tokens**: Escalable para microservicios
- ✅ **Base de datos**: PostgreSQL para alto rendimiento
- ✅ **Internacionalización**: Fácil agregar idiomas
- ✅ **Modelos extensibles**: Fácil agregar campos

### **🚀 PRÓXIMAS FUNCIONALIDADES:**
- 📊 Módulos contables (facturas, reportes)
- 📱 App móvil nativa
- 🔗 Integración con APIs gubernamentales
- 📈 Dashboard de analytics
- 🤖 Automatización contable

---

## 📞 **SOPORTE Y MANTENIMIENTO**

### **🐛 DEBUGGING:**
- **Logs**: Django logging configurado
- **Debug Toolbar**: Para desarrollo
- **Error Tracking**: Preparado para Sentry
- **Performance**: Django Debug Toolbar

### **🧪 TESTING:**
- **Scripts de Prueba**: Validación JWT, email, registro
- **Unit Tests**: Preparado para pytest
- **API Testing**: Scripts curl y Python
- **Load Testing**: Preparado para locust

---

## 📚 **DOCUMENTACIÓN ADICIONAL**

- **COMANDOS_POWERSHELL.md**: Comandos específicos para Windows
- **MIGRACIONES_Y_EJECUCION.md**: Guía paso a paso
- **API_DOCUMENTATION.md**: Documentación completa de API
- **REGISTRO_COLOMBIANO.md**: Validaciones específicas

---

**🎉 S_CONTABLE está listo para producción y escalamiento futuro con una base sólida, segura y específicamente diseñada para el mercado colombiano.**
