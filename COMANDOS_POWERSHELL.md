# 💻 S_CONTABLE - COMANDOS IMPORTANTES DE POWERSHELL

## 🎯 **GUÍA COMPLETA DE COMANDOS PARA WINDOWS**

---

## 🚀 **COMANDOS BÁSICOS DE PROYECTO**

### **🔧 CONFIGURACIÓN INICIAL**

```powershell
# Navegar al directorio del proyecto
cd C:\Users\ASUS\S_CONTABLE

# Verificar contenido del directorio
ls
# o
Get-ChildItem

# Mostrar estructura de directorios
tree /F

# Verificar versión de Python
python --version

# Verificar pip
pip --version
```

### **🐍 GESTIÓN DE ENTORNO VIRTUAL**

```powershell
# Crear entorno virtual (solo la primera vez)
python -m venv env

# Activar entorno virtual (SIEMPRE antes de trabajar)
.\env\Scripts\Activate.ps1

# Verificar que está activado (debe mostrar (env) al inicio)
# El prompt debe cambiar a: (env) PS C:\Users\ASUS\S_CONTABLE>

# Desactivar entorno virtual
deactivate

# Verificar paquetes instalados
pip list

# Instalar dependencias desde requirements.txt
pip install -r requirements.txt

# Actualizar pip
python -m pip install --upgrade pip
```

### **⚠️ SOLUCIÓN DE PROBLEMAS DE EJECUCIÓN**

```powershell
# Si aparece error de "execution policy"
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verificar política actual
Get-ExecutionPolicy

# Alternativa para activar entorno (si falla el anterior)
& ".\env\Scripts\Activate.ps1"

# O usar cmd dentro de PowerShell
cmd
.\env\Scripts\activate.bat
```

---

## 🗄️ **COMANDOS DE BASE DE DATOS Y MIGRACIONES**

### **📊 MIGRACIONES**

```powershell
# SIEMPRE activar entorno virtual primero
.\env\Scripts\Activate.ps1

# Verificar estado de migraciones
python manage.py showmigrations

# Ver migraciones pendientes
python manage.py showmigrations --plan

# Crear migraciones automáticamente
python manage.py makemigrations

# Crear migración para app específica
python manage.py makemigrations accounts

# Aplicar todas las migraciones
python manage.py migrate

# Aplicar migraciones de app específica
python manage.py migrate accounts

# Ver SQL de una migración específica
python manage.py sqlmigrate accounts 0001

# Migración en seco (simular sin aplicar)
python manage.py migrate --dry-run

# Revertir a migración específica
python manage.py migrate accounts 0001

# Marcar migración como aplicada sin ejecutar (CUIDADO)
python manage.py migrate accounts 0001 --fake
```

### **🔧 GESTIÓN DE BASE DE DATOS**

```powershell
# Abrir shell de base de datos
python manage.py dbshell

# Crear superusuario
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword nombre_usuario

# Exportar datos a JSON
python manage.py dumpdata > backup.json

# Exportar app específica
python manage.py dumpdata accounts > accounts_backup.json

# Cargar datos desde JSON
python manage.py loaddata backup.json

# Limpiar sesiones expiradas
python manage.py clearsessions
```

---

## 🌐 **COMANDOS DE SERVIDOR Y DESARROLLO**

### **🚀 EJECUTAR SERVIDOR**

```powershell
# Activar entorno virtual
.\env\Scripts\Activate.ps1

# Verificar configuración antes de ejecutar
python manage.py check

# Ejecutar servidor en puerto por defecto (8000)
python manage.py runserver

# Ejecutar en puerto específico
python manage.py runserver 8080

# Ejecutar accesible desde red local
python manage.py runserver 0.0.0.0:8000

# Ejecutar con verbosidad alta (más logs)
python manage.py runserver --verbosity=2

# Ejecutar sin recarga automática
python manage.py runserver --noreload
```

### **🔍 DEBUGGING Y LOGS**

```powershell
# Shell interactivo de Django
python manage.py shell

# Verificar configuración completa
python manage.py check

# Verificar configuración para producción
python manage.py check --deploy

# Ver todas las URLs disponibles
python manage.py show_urls

# Recopilar archivos estáticos
python manage.py collectstatic

# Verificar archivos estáticos
python manage.py findstatic admin/css/base.css
```

---

## 🧪 **COMANDOS DE TESTING Y VALIDACIÓN**

### **🔐 VALIDACIÓN JWT**

```powershell
# Activar entorno virtual
.\env\Scripts\Activate.ps1

# Ejecutar script de validación JWT completo
python manual_jwt_validation.py

# Ejecutar validación JWT simple
python test_jwt_simple.py

# Probar configuración de email
python verificar_email.py

# Probar validación de contraseñas
python test_password_validation.py

# Probar URLs del sistema
python test_urls.py
```

### **📧 TESTING DE EMAIL**

```powershell
# Probar configuración de email
python verificar_email.py

# Enviar email de prueba
python test_email.py

# Verificar variables de entorno de email
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(f'EMAIL_HOST_USER: {os.getenv(\"EMAIL_HOST_USER\")}'); print(f'EMAIL_HOST_PASSWORD: {\"CONFIGURADO\" if os.getenv(\"EMAIL_HOST_PASSWORD\") else \"NO CONFIGURADO\"}')"
```

### **🌐 TESTING DE API**

```powershell
# Probar endpoints de API usando PowerShell nativo

# 1. Registrar usuario
$userData = @{
    username = "test_user"
    email = "test@example.com"
    password1 = "TestPass123!"
    password2 = "TestPass123!"
    first_name = "Test"
    last_name = "User"
    tipo_documento = "CC"
    numero_documento = "1234567890"
    telefono = "3001234567"
    acepta_terminos = $true
    acepta_politica_privacidad = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/registro-completo/" -Method POST -Body $userData -ContentType "application/json"

# 2. Obtener token JWT
$loginData = @{
    username = "test_user"
    password = "TestPass123!"
} | ConvertTo-Json

$tokens = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/token/" -Method POST -Body $loginData -ContentType "application/json"
$accessToken = $tokens.access

# 3. Probar API autenticada
$headers = @{
    "Authorization" = "Bearer $accessToken"
}

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Method GET -Headers $headers
```

---

## 📁 **COMANDOS DE GESTIÓN DE ARCHIVOS**

### **🔍 EXPLORACIÓN DE ARCHIVOS**

```powershell
# Listar archivos con detalles
Get-ChildItem -Force

# Buscar archivos por extensión
Get-ChildItem -Recurse -Include "*.py"

# Buscar archivos por nombre
Get-ChildItem -Recurse -Name "*models*"

# Ver contenido de archivo
Get-Content archivo.py

# Ver primeras 10 líneas
Get-Content archivo.py -Head 10

# Ver últimas 10 líneas
Get-Content archivo.py -Tail 10

# Buscar texto en archivos
Select-String -Pattern "JWT" -Path "*.py" -Recurse
```

### **📝 EDICIÓN Y CREACIÓN DE ARCHIVOS**

```powershell
# Crear archivo vacío
New-Item -ItemType File -Name "nuevo_archivo.py"

# Crear directorio
New-Item -ItemType Directory -Name "nuevo_directorio"

# Copiar archivo
Copy-Item "archivo.py" "archivo_backup.py"

# Mover archivo
Move-Item "archivo.py" "nueva_ubicacion/"

# Eliminar archivo (CUIDADO)
Remove-Item "archivo.py"

# Eliminar directorio y contenido (CUIDADO)
Remove-Item "directorio" -Recurse -Force

# Abrir archivo en editor por defecto
Invoke-Item "archivo.py"

# Abrir archivo en notepad
notepad archivo.py
```

---

## 🔧 **COMANDOS DE CONFIGURACIÓN Y VARIABLES**

### **🌍 VARIABLES DE ENTORNO**

```powershell
# Ver todas las variables de entorno
Get-ChildItem Env:

# Ver variable específica
$env:PATH

# Establecer variable temporal (solo para sesión actual)
$env:DJANGO_SETTINGS_MODULE = "core.settings"

# Ver contenido del archivo .env
Get-Content .env

# Verificar si archivo .env existe
Test-Path .env

# Crear archivo .env básico
@"
DEBUG=True
SECRET_KEY=tu-secret-key
DATABASE_URL=tu-database-url
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
"@ | Out-File -FilePath .env -Encoding utf8
```

### **🔍 INFORMACIÓN DEL SISTEMA**

```powershell
# Ver información del sistema
Get-ComputerInfo

# Ver versión de Windows
Get-WmiObject -Class Win32_OperatingSystem | Select-Object Version, Caption

# Ver información de Python
python -c "import sys; print(f'Python {sys.version}')"

# Ver información de Django
python -c "import django; print(f'Django {django.get_version()}')"

# Ver espacio en disco
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace

# Ver procesos de Python ejecutándose
Get-Process python*
```

---

## 🌐 **COMANDOS DE RED Y CONECTIVIDAD**

### **🔗 TESTING DE CONECTIVIDAD**

```powershell
# Probar conexión a servidor local
Test-NetConnection -ComputerName 127.0.0.1 -Port 8000

# Ver puertos en uso
netstat -ano | findstr :8000

# Terminar proceso por PID
taskkill /PID <numero_pid> /F

# Probar conexión a base de datos (si es local)
Test-NetConnection -ComputerName localhost -Port 5432

# Verificar DNS
nslookup google.com

# Ping a servidor
ping 127.0.0.1
```

### **📡 CURL ALTERNATIVO CON POWERSHELL**

```powershell
# GET request
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Method GET

# POST request con JSON
$body = @{key="value"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/endpoint/" -Method POST -Body $body -ContentType "application/json"

# Request con headers
$headers = @{"Authorization"="Bearer token"}
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/me/" -Headers $headers

# Descargar archivo
Invoke-WebRequest -Uri "http://example.com/file.zip" -OutFile "file.zip"
```

---

## 🚨 **COMANDOS DE EMERGENCIA Y SOLUCIÓN DE PROBLEMAS**

### **🔧 RESETEAR PROYECTO**

```powershell
# CUIDADO: Estos comandos eliminan datos

# 1. Desactivar entorno virtual
deactivate

# 2. Eliminar entorno virtual
Remove-Item -Recurse -Force env

# 3. Crear nuevo entorno virtual
python -m venv env

# 4. Activar nuevo entorno
.\env\Scripts\Activate.ps1

# 5. Instalar dependencias
pip install -r requirements.txt

# 6. Resetear migraciones (ELIMINA DATOS)
Remove-Item accounts\migrations\0*.py
python manage.py makemigrations
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser
```

### **🧹 LIMPIEZA DE ARCHIVOS TEMPORALES**

```powershell
# Limpiar archivos .pyc
Get-ChildItem -Recurse -Include "*.pyc" | Remove-Item -Force

# Limpiar directorios __pycache__
Get-ChildItem -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force

# Limpiar archivos temporales de Windows
Remove-Item -Path $env:TEMP\* -Recurse -Force -ErrorAction SilentlyContinue

# Limpiar logs de Django (si existen)
Remove-Item -Path "logs\*" -Force -ErrorAction SilentlyContinue
```

### **🔍 DIAGNÓSTICO DE PROBLEMAS**

```powershell
# Verificar que Python funciona
python -c "print('Python funciona correctamente')"

# Verificar que Django está instalado
python -c "import django; print(f'Django {django.get_version()} instalado')"

# Verificar configuración de Django
python manage.py check --verbosity=2

# Ver configuración actual de Django
python manage.py diffsettings

# Verificar conexión a base de datos
python manage.py dbshell --version

# Ver logs de errores recientes (si existen)
Get-EventLog -LogName Application -Source Python* -Newest 10
```

---

## 📚 **COMANDOS DE INFORMACIÓN Y AYUDA**

### **❓ OBTENER AYUDA**

```powershell
# Ayuda de comando Django
python manage.py help

# Ayuda de comando específico
python manage.py help migrate

# Listar todos los comandos disponibles
python manage.py help --commands

# Ayuda de PowerShell
Get-Help Get-ChildItem

# Ayuda con ejemplos
Get-Help Get-ChildItem -Examples

# Manual completo de comando
Get-Help Get-ChildItem -Full
```

### **📊 INFORMACIÓN DEL PROYECTO**

```powershell
# Ver configuración actual
python manage.py diffsettings

# Ver todas las URLs
python manage.py show_urls

# Ver información de apps instaladas
python -c "from django.conf import settings; print('\n'.join(settings.INSTALLED_APPS))"

# Ver información de middleware
python -c "from django.conf import settings; print('\n'.join(settings.MIDDLEWARE))"

# Ver configuración de base de datos
python -c "from django.conf import settings; print(settings.DATABASES)"
```

---

## 🎯 **COMANDOS RÁPIDOS DE USO DIARIO**

### **⚡ WORKFLOW TÍPICO**

```powershell
# 1. Navegar al proyecto
cd C:\Users\ASUS\S_CONTABLE

# 2. Activar entorno
.\env\Scripts\Activate.ps1

# 3. Verificar y aplicar migraciones
python manage.py showmigrations
python manage.py migrate

# 4. Ejecutar servidor
python manage.py runserver

# 5. En otra terminal: probar funcionalidades
python verificar_email.py
python test_jwt_simple.py
```

### **🔄 COMANDOS DE ACTUALIZACIÓN**

```powershell
# Actualizar dependencias
pip list --outdated
pip install --upgrade django
pip freeze > requirements.txt

# Actualizar pip
python -m pip install --upgrade pip

# Verificar seguridad de dependencias
pip audit
```

---

## 🎉 **COMANDOS DE PRODUCTIVIDAD**

### **⌨️ ALIASES ÚTILES**

```powershell
# Crear aliases para comandos frecuentes (en perfil de PowerShell)
Set-Alias -Name activate -Value ".\env\Scripts\Activate.ps1"
Set-Alias -Name runserver -Value "python manage.py runserver"
Set-Alias -Name migrate -Value "python manage.py migrate"
Set-Alias -Name shell -Value "python manage.py shell"

# Ver perfil de PowerShell
$PROFILE

# Editar perfil (agregar aliases permanentes)
notepad $PROFILE
```

### **📋 SCRIPTS DE AUTOMATIZACIÓN**

```powershell
# Script para inicio rápido (guardar como start_project.ps1)
@"
cd C:\Users\ASUS\S_CONTABLE
.\env\Scripts\Activate.ps1
python manage.py check
python manage.py migrate
python manage.py runserver
"@ | Out-File -FilePath start_project.ps1

# Ejecutar script
.\start_project.ps1
```

---

**💡 CONSEJO: Guarda estos comandos en un archivo de texto para referencia rápida. Los comandos más importantes son los de activación del entorno virtual, migraciones y ejecución del servidor.**

**🎯 COMANDOS ESENCIALES DIARIOS:**
1. `.\env\Scripts\Activate.ps1` - Activar entorno
2. `python manage.py migrate` - Aplicar migraciones
3. `python manage.py runserver` - Ejecutar servidor
4. `python verificar_email.py` - Probar email
5. `python test_jwt_simple.py` - Probar JWT
