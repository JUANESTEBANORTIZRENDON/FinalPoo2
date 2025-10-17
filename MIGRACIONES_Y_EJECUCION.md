# 🚀 S_CONTABLE - MIGRACIONES Y EJECUCIÓN

## 📋 **GUÍA COMPLETA DE CONFIGURACIÓN Y EJECUCIÓN**

---

## 🔧 **CONFIGURACIÓN INICIAL DEL PROYECTO**

### **1️⃣ CLONAR Y CONFIGURAR ENTORNO**

```powershell
# 1. Navegar al directorio del proyecto
cd C:\Users\ASUS\S_CONTABLE

# 2. Crear entorno virtual (si no existe)
python -m venv env

# 3. Activar entorno virtual
.\env\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
pip list
```

### **2️⃣ CONFIGURAR VARIABLES DE ENTORNO**

```powershell
# Crear archivo .env en la raíz del proyecto
# Contenido del archivo .env:
```

```env
# Configuración de Django
DEBUG=True
SECRET_KEY=django-insecure-rc*ay)v)t(t9fxzait3el=$=sz_-bmm^hdvcgqs#-54lwre2=h

# Base de Datos Neon PostgreSQL
DATABASE_URL=postgresql://neondb_owner:npg_qPCFG5v2tgRf@ep-dry-sound-ad82eq4g-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Configuración de Email Gmail
EMAIL_HOST_USER=juanestebanortizrendon24072004@gmail.com
EMAIL_HOST_PASSWORD=kjhdtevybncwbxfe

# Configuración de Seguridad
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

---

## 🗄️ **SISTEMA DE MIGRACIONES**

### **📊 ¿QUÉ SON LAS MIGRACIONES?**

Las migraciones son **archivos Python** que contienen instrucciones para:
- ✅ Crear tablas en la base de datos
- ✅ Modificar estructura de tablas existentes
- ✅ Agregar/eliminar campos
- ✅ Crear índices y relaciones
- ✅ Poblar datos iniciales

### **🔍 VERIFICAR ESTADO DE MIGRACIONES**

```powershell
# Activar entorno virtual
.\env\Scripts\Activate.ps1

# Ver migraciones pendientes
python manage.py showmigrations

# Ver migraciones aplicadas (con [X])
python manage.py showmigrations --list

# Ver SQL que se ejecutará
python manage.py sqlmigrate accounts 0001
```

### **📝 CREAR NUEVAS MIGRACIONES**

```powershell
# Crear migraciones automáticamente (detecta cambios en models.py)
python manage.py makemigrations

# Crear migración específica para una app
python manage.py makemigrations accounts

# Crear migración con nombre personalizado
python manage.py makemigrations accounts --name agregar_campo_profesion

# Crear migración vacía (para datos personalizados)
python manage.py makemigrations accounts --empty --name poblar_datos_iniciales
```

### **🚀 APLICAR MIGRACIONES**

```powershell
# Aplicar TODAS las migraciones pendientes
python manage.py migrate

# Aplicar migraciones de una app específica
python manage.py migrate accounts

# Aplicar hasta una migración específica
python manage.py migrate accounts 0001

# Simular migración (ver qué se haría sin ejecutar)
python manage.py migrate --dry-run

# Ver SQL que se ejecutará
python manage.py migrate --verbosity=2
```

### **⚠️ PROBLEMAS COMUNES CON MIGRACIONES**

#### **Problema 1: Migración Conflictiva**
```powershell
# Error: "Conflicting migrations detected"
# Solución: Fusionar migraciones
python manage.py makemigrations --merge
```

#### **Problema 2: Migración Falsa**
```powershell
# Marcar migración como aplicada sin ejecutar
python manage.py migrate accounts 0001 --fake

# Marcar TODAS como aplicadas (PELIGROSO)
python manage.py migrate --fake
```

#### **Problema 3: Revertir Migración**
```powershell
# Revertir a migración anterior
python manage.py migrate accounts 0001

# Revertir TODAS las migraciones de una app
python manage.py migrate accounts zero
```

#### **Problema 4: Resetear Base de Datos**
```powershell
# ⚠️ CUIDADO: Esto ELIMINA todos los datos

# 1. Eliminar archivo de base de datos (si es SQLite)
Remove-Item db.sqlite3

# 2. Eliminar archivos de migración (mantener __init__.py)
Remove-Item accounts\migrations\0*.py

# 3. Crear migraciones desde cero
python manage.py makemigrations

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser
```

---

## 🏃‍♂️ **EJECUCIÓN DEL PROYECTO**

### **🚀 INICIO RÁPIDO**

```powershell
# 1. Activar entorno virtual
.\env\Scripts\Activate.ps1

# 2. Verificar configuración
python manage.py check

# 3. Aplicar migraciones
python manage.py migrate

# 4. Crear superusuario (si no existe)
python manage.py createsuperuser

# 5. Ejecutar servidor de desarrollo
python manage.py runserver

# 6. Abrir navegador en: http://127.0.0.1:8000
```

### **🔧 COMANDOS DE DESARROLLO**

#### **Servidor de Desarrollo:**
```powershell
# Servidor en puerto por defecto (8000)
python manage.py runserver

# Servidor en puerto específico
python manage.py runserver 8080

# Servidor accesible desde red local
python manage.py runserver 0.0.0.0:8000

# Servidor con recarga automática (por defecto)
python manage.py runserver --noreload
```

#### **Shell Interactivo:**
```powershell
# Shell de Django (con modelos cargados)
python manage.py shell

# Shell con IPython (más funcional)
pip install ipython
python manage.py shell

# Ejecutar script Python en contexto Django
python manage.py shell < script.py
```

#### **Gestión de Datos:**
```powershell
# Crear superusuario
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword username

# Cargar datos desde fixture
python manage.py loaddata fixture.json

# Exportar datos a fixture
python manage.py dumpdata accounts.PerfilUsuario > perfiles.json
```

---

## 🧪 **VALIDACIÓN JWT EN TIEMPO REAL**

### **📋 PROCESO COMPLETO DE VALIDACIÓN**

#### **1️⃣ PREPARACIÓN**
```powershell
# Asegurarse de que el servidor esté ejecutándose
python manage.py runserver

# En otra terminal, activar entorno
.\env\Scripts\Activate.ps1
```

#### **2️⃣ CREAR USUARIO EN LA INTERFAZ WEB**

1. **Abrir navegador**: http://127.0.0.1:8000/accounts/register/
2. **Llenar formulario** con datos válidos:
   - Username: `jwt_test_user`
   - Email: `jwt_test@example.com`
   - Contraseña: `TestPassword123!`
   - Documento: CC - 1234567890
   - Teléfono: 3001234567
   - Aceptar términos y condiciones
3. **Registrar usuario** → Se envía email de activación
4. **Activar usuario manualmente** (para pruebas):

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.get(username='jwt_test_user')
user.is_active = True
user.save()
print("Usuario activado")
exit()
```

#### **3️⃣ VALIDAR JWT EN TERMINAL**

##### **Paso 1: Obtener Token JWT**
```powershell
# Usar PowerShell nativo
$loginData = @{
    username = "jwt_test_user"
    password = "TestPassword123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $loginData -ContentType "application/json"

$accessToken = $response.access
$refreshToken = $response.refresh

Write-Host "Access Token: $accessToken"
Write-Host "Refresh Token: $refreshToken"
```

##### **Paso 2: Probar API con Token**
```powershell
$headers = @{
    "Authorization" = "Bearer $accessToken"
}

$userInfo = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Method GET -Headers $headers
$userInfo | ConvertTo-Json -Depth 3
```

##### **Paso 3: Cambiar Contraseña en Interfaz Web**
1. **Ir a**: http://127.0.0.1:8000/accounts/password_reset/
2. **Ingresar email**: jwt_test@example.com
3. **Seguir enlace del email** (revisar bandeja de entrada)
4. **Cambiar contraseña** a: `NewPassword456!`

##### **Paso 4: Obtener Nuevo Token**
```powershell
$newLoginData = @{
    username = "jwt_test_user"
    password = "NewPassword456!"
} | ConvertTo-Json

$newResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $newLoginData -ContentType "application/json"

$newAccessToken = $newResponse.access
Write-Host "Nuevo Access Token: $newAccessToken"
```

##### **Paso 5: Comparar Tokens**
```powershell
if ($accessToken -ne $newAccessToken) {
    Write-Host "✅ ÉXITO: Los tokens son diferentes"
    Write-Host "🔐 JWT funciona correctamente - los tokens cambian al cambiar contraseña"
} else {
    Write-Host "❌ ERROR: Los tokens son iguales"
}
```

##### **Paso 6: Limpiar Usuario de Prueba**
```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User
User.objects.get(username='jwt_test_user').delete()
print("Usuario de prueba eliminado")
exit()
```

---

## 🔧 **SCRIPTS DE AUTOMATIZACIÓN**

### **📝 SCRIPT DE VALIDACIÓN AUTOMÁTICA**

```powershell
# Ejecutar script completo de validación
python manual_jwt_validation.py

# Ejecutar script de prueba de email
python verificar_email.py

# Ejecutar script de validación de contraseñas
python test_password_validation.py
```

### **🧹 SCRIPTS DE MANTENIMIENTO**

```powershell
# Limpiar archivos temporales
python manage.py clearsessions

# Recopilar archivos estáticos
python manage.py collectstatic

# Verificar configuración
python manage.py check --deploy

# Crear backup de base de datos
python manage.py dumpdata > backup.json
```

---

## 🚨 **SOLUCIÓN DE PROBLEMAS COMUNES**

### **❌ Error: "No module named 'django'"**
```powershell
# Solución: Activar entorno virtual
.\env\Scripts\Activate.ps1
pip install django
```

### **❌ Error: "CSRF verification failed"**
```powershell
# Solución: Verificar CSRF_TRUSTED_ORIGINS en .env
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
```

### **❌ Error: "Database connection failed"**
```powershell
# Solución: Verificar DATABASE_URL en .env
# Probar conexión:
python manage.py dbshell
```

### **❌ Error: "Email backend not configured"**
```powershell
# Solución: Verificar configuración de email en .env
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=contraseña-de-aplicacion
```

### **❌ Error: "Port already in use"**
```powershell
# Solución: Usar puerto diferente
python manage.py runserver 8080

# O terminar proceso que usa el puerto
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📊 **MONITOREO Y LOGS**

### **📝 LOGS DE DESARROLLO**

```powershell
# Ver logs en tiempo real
python manage.py runserver --verbosity=2

# Logs de migraciones
python manage.py migrate --verbosity=2

# Logs de comandos personalizados
python manage.py <comando> --verbosity=3
```

### **🔍 DEBUGGING**

```python
# En views.py o cualquier archivo Python
import logging
logger = logging.getLogger(__name__)

def mi_vista(request):
    logger.debug("Debug info")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

---

## 🎯 **CHECKLIST DE DESPLIEGUE**

### **✅ ANTES DE PRODUCCIÓN**

```powershell
# 1. Verificar configuración
python manage.py check --deploy

# 2. Aplicar migraciones
python manage.py migrate

# 3. Recopilar archivos estáticos
python manage.py collectstatic

# 4. Crear superusuario
python manage.py createsuperuser

# 5. Probar funcionalidades críticas
python test_jwt_simple.py
python verificar_email.py

# 6. Configurar variables de producción
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com
```

---

**🎉 Con esta guía tienes todo lo necesario para configurar, migrar y ejecutar S_CONTABLE correctamente, incluyendo la validación completa del sistema JWT.**
