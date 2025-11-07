# 🔐 Cambio de Contraseña del Administrador Django

## 📋 Descripción
Este documento describe el proceso para cambiar/resetear la contraseña del superusuario de Django cuando no recuerdas la contraseña anterior.

---

## ⚡ Cambio Rápido de Contraseña

### Método 1: Cambiar Contraseña de un Usuario Existente (Recomendado)

Este método te permite cambiar la contraseña sin necesitar la contraseña anterior.

#### Paso 1: Activar el entorno virtual
```bash
.\env\Scripts\Activate.ps1
```

#### Paso 2: Ejecutar el comando de cambio de contraseña
```bash
python manage.py changepassword admin
```

#### Paso 3: Ingresar la nueva contraseña
El sistema te pedirá que ingreses la nueva contraseña dos veces:
```
Changing password for user 'admin'
Password: [ingresa tu nueva contraseña]
Password (again): [ingresa la misma contraseña]
Password changed successfully for user 'admin'
```

**✅ ¡Listo! Ya puedes acceder con tu nueva contraseña.**

---

## 🛠️ Método 2: Usando el Shell de Django

Si prefieres usar el shell interactivo de Django:

#### Paso 1: Activar el entorno virtual
```bash
.\env\Scripts\Activate.ps1
```

#### Paso 2: Abrir el shell de Django
```bash
python manage.py shell
```

#### Paso 3: Ejecutar los siguientes comandos en el shell
```python
from django.contrib.auth.models import User

# Obtener el usuario admin
user = User.objects.get(username='admin')

# Establecer la nueva contraseña
user.set_password('TuNuevaContraseña123!')

# Guardar los cambios
user.save()

# Salir del shell
exit()
```

**✅ ¡Listo! La contraseña ha sido cambiada.**

---

## 🔄 Método 3: Crear un Nuevo Superusuario

Si prefieres crear un nuevo superusuario desde cero:

#### Paso 1: Activar el entorno virtual
```bash
.\env\Scripts\Activate.ps1
```

#### Paso 2: Ejecutar el comando createsuperuser
```bash
python manage.py createsuperuser
```

#### Paso 3: Completar los datos solicitados
```
Username: admin2
Email address: admin2@scontable.com
Password: [ingresa tu contraseña]
Password (again): [confirma tu contraseña]
Superuser created successfully.
```

---

## 📝 Credenciales de Acceso Actuales

### Panel de Administración Django
- **URL**: http://127.0.0.1:8000/admin/
- **Usuario**: `admin`
- **Contraseña**: `[La que acabas de cambiar]`

### Panel de Administrador Holding
- **URL**: http://127.0.0.1:8000/empresas/dev-auth/
- **Contraseña Adicional Desarrollador**: `dev2025secure!`
  - Esta es una contraseña adicional de seguridad para acceder al panel de desarrollador
  - Es diferente a la contraseña del usuario admin

---

## 🔒 Contraseña del Panel Desarrollador

El panel de desarrollador (`/empresas/dev-auth/`) tiene una contraseña adicional de seguridad configurada en el código. Si necesitas cambiarla:

### Ubicación del archivo
```
empresas/views_dev_auth.py
```

### Cambiar la contraseña de desarrollador
Busca la línea que contiene:
```python
DEV_PASSWORD = "dev2025secure!"
```

Y cámbiala por tu nueva contraseña:
```python
DEV_PASSWORD = "TuNuevaContraseñaDesarrollador123!"
```

**⚠️ Importante**: Esta contraseña está hardcodeada por seguridad adicional. Es diferente de la contraseña del usuario Django.

---

## ✅ Verificar el Cambio

### Paso 1: Iniciar el servidor
```bash
python manage.py runserver
```

### Paso 2: Acceder al admin
Abre tu navegador y ve a: **http://127.0.0.1:8000/admin/**

### Paso 3: Ingresar credenciales
- Usuario: `admin`
- Contraseña: `[Tu nueva contraseña]`

Si puedes acceder correctamente, ¡el cambio fue exitoso! ✅

---

## 🚨 Solución de Problemas

### Error: "User matching query does not exist"
**Problema**: No existe un usuario con ese nombre.

**Solución**: Verifica el nombre del usuario o crea uno nuevo con `createsuperuser`.

### Error: "Password too similar to username"
**Problema**: Django requiere contraseñas más seguras.

**Solución**: Usa una contraseña que:
- Tenga al menos 8 caracteres
- Combine letras, números y símbolos
- No sea similar al nombre de usuario

### La contraseña no funciona después del cambio
**Problema**: Puede que no se haya guardado correctamente.

**Solución**: Repite el proceso usando el Método 2 (Shell de Django) y asegúrate de llamar `user.save()`.

---

## 📌 Recomendaciones de Seguridad

1. ✅ **Usa contraseñas fuertes**: Combina mayúsculas, minúsculas, números y símbolos
2. ✅ **No compartas las contraseñas**: Mantén las credenciales privadas
3. ✅ **Documenta los cambios**: Anota las nuevas credenciales en un lugar seguro
4. ✅ **No subas contraseñas al repositorio**: Usa variables de entorno para producción
5. ✅ **Cambia las contraseñas por defecto**: Especialmente en producción

---

## 📅 Historial de Cambios

| Fecha | Usuario | Cambio Realizado |
|-------|---------|------------------|
| 06/11/2025 | Sistema | Documento creado con procedimientos de cambio de contraseña |

---

## 📞 Contacto

Si tienes problemas adicionales, consulta:
- `README.md` - Comandos esenciales del proyecto
- `COMANDOS_ESENCIALES.md` - Guía rápida de comandos
- Documentación de Django: https://docs.djangoproject.com/
