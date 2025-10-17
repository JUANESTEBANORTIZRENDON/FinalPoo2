# 📚 **COMANDOS ESENCIALES DE DJANGO - S_CONTABLE**

## 🚀 **Comandos Básicos de Desarrollo**

### **1. Activar Entorno Virtual**
```bash
# Siempre ejecutar PRIMERO
.\env\Scripts\Activate.ps1
```

### **2. Gestión de Base de Datos**
```bash
# Crear migraciones (cuando cambias modelos)
python manage.py makemigrations

# Aplicar migraciones a la base de datos
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations

# Ver SQL de una migración específica
python manage.py sqlmigrate accounts 0001

# Resetear migraciones (CUIDADO - solo en desarrollo)
python manage.py migrate accounts zero
```

### **3. Gestión de Usuarios**
```bash
# Crear superusuario (administrador)
python manage.py createsuperuser

# Cambiar contraseña de usuario
python manage.py changepassword admin

# Crear usuario programáticamente
python crear_superusuario.py
```

### **4. Servidor de Desarrollo**
```bash
# Ejecutar servidor (puerto 8000 por defecto)
python manage.py runserver

# Ejecutar en puerto específico
python manage.py runserver 8080

# Ejecutar en IP específica
python manage.py runserver 0.0.0.0:8000
```

### **5. Gestión de Aplicaciones**
```bash
# Crear nueva aplicación
python manage.py startapp nombre_app

# Instalar dependencias
pip install -r requirements.txt

# Actualizar requirements.txt
pip freeze > requirements.txt
```

## 🔧 **Comandos de Diagnóstico**

### **6. Verificar Configuración**
```bash
# Verificar configuración del proyecto
python manage.py check

# Verificar configuración de base de datos
python manage.py dbshell

# Abrir shell de Django
python manage.py shell
```

### **7. Gestión de Archivos Estáticos**
```bash
# Recopilar archivos estáticos (para producción)
python manage.py collectstatic

# Limpiar archivos estáticos
python manage.py collectstatic --clear
```

## 🗄️ **Comandos de Base de Datos Específicos**

### **8. Inspeccionar Base de Datos**
```bash
# Ver estructura de la base de datos
python manage.py inspectdb

# Crear fixtures (respaldo de datos)
python manage.py dumpdata > backup.json

# Cargar fixtures
python manage.py loaddata backup.json
```

### **9. Comandos Personalizados del Proyecto**
```bash
# Crear superusuario automáticamente
python crear_superusuario.py


# Configurar proyecto completo
.\setup_project.ps1
```

## 🚨 **Comandos de Emergencia**

### **10. Solución de Problemas**
```bash
# Limpiar archivos .pyc
python -c "import py_compile; py_compile.compile('manage.py')"

# Verificar dependencias
pip check

# Reinstalar dependencias
pip install --force-reinstall -r requirements.txt

# Resetear base de datos (CUIDADO)
python manage.py flush
```

## 📋 **Flujo de Trabajo Típico**

### **Desarrollo Diario:**
```bash
# 1. Activar entorno
.\env\Scripts\Activate.ps1

# 2. Verificar estado
python manage.py check

# 3. Aplicar migraciones pendientes
python manage.py migrate

# 4. Ejecutar servidor
python manage.py runserver
```

### **Después de Cambios en Modelos:**
```bash
# 1. Crear migraciones
python manage.py makemigrations

# 2. Ver qué va a cambiar
python manage.py showmigrations

# 3. Aplicar cambios
python manage.py migrate

# 4. Verificar en admin
# Ir a: http://127.0.0.1:8000/admin/
```

### **Configurar Nuevo Entorno:**
```bash
# 1. Clonar proyecto
git clone <repositorio>

# 2. Crear entorno virtual
python -m venv env

# 3. Activar entorno
.\env\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar .env
# Copiar .env.example como .env y editar

# 6. Aplicar migraciones
python manage.py migrate

# 7. Crear superusuario
python crear_superusuario.py

# 8. Ejecutar servidor
python manage.py runserver
```

## 🎯 **Comandos Específicos de S_CONTABLE**

### **Credenciales del Superusuario:**
- **Usuario**: `admin`
- **Contraseña**: `Admin123!`
- **Email**: `admin@scontable.com`

### **URLs Importantes:**
- **Admin**: http://127.0.0.1:8000/admin/
- **Login**: http://127.0.0.1:8000/accounts/login/
- **Registro**: http://127.0.0.1:8000/accounts/register/
- **API**: http://127.0.0.1:8000/api/

### **Archivos de Configuración:**
- **`.env`**: Variables de entorno (NO subir al repositorio)
- **`requirements.txt`**: Dependencias del proyecto
- **`manage.py`**: Comando principal de Django

## 💡 **Tips Importantes**

1. **Siempre activar el entorno virtual primero**
2. **Hacer migraciones después de cambiar modelos**
3. **Verificar configuración con `python manage.py check`**
4. **Usar `python crear_superusuario.py` si falla el comando normal**
5. **El archivo `.env` contiene información sensible - NO subirlo**
6. **Hacer backup de la base de datos antes de cambios importantes**

## 🔒 **Seguridad**

- **Nunca subir `.env` al repositorio**
- **Cambiar `SECRET_KEY` en producción**
- **Usar HTTPS en producción**
- **Mantener dependencias actualizadas**
- **Hacer backups regulares de la base de datos**
