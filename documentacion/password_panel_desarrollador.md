# 🔒 Contraseña del Panel de Desarrollador

## 📋 Información General

El Sistema S_CONTABLE tiene **dos niveles de autenticación** para acceder al panel técnico de Django Admin:

1. **Primera capa**: Usuario y contraseña de Django (el usuario `admin`)
2. **Segunda capa**: Contraseña adicional del panel de desarrollador

Esta segunda capa protege el acceso técnico al sistema y solo está disponible para administradores del holding.

---

## 🔐 Contraseña Actual

**Contraseña del Panel Desarrollador:** `hackerputo24`

**URL de acceso:** http://127.0.0.1:8000/empresas/dev-auth/

**Ubicación de configuración:** Archivo `.env` (raíz del proyecto)

---

## ⚡ Cómo Cambiar la Contraseña

### Método: Editar el archivo .env (Recomendado)

#### Paso 1: Ubicar el archivo
El archivo `.env` está en la raíz del proyecto:
```
FinalPoo2/
├── .env          ← Aquí está el archivo
├── manage.py
├── core/
└── ...
```

#### Paso 2: Abrir el archivo .env
Puedes abrirlo con cualquier editor de texto:
- Visual Studio Code
- Notepad
- Notepad++
- etc.

#### Paso 3: Buscar la variable DJANGO_DEV_PASSWORD
```bash
# ==================================================
# 🔒 PANEL DE DESARROLLADOR
# ==================================================

# DJANGO_DEV_PASSWORD: Contraseña adicional para acceder al panel Django Admin
DJANGO_DEV_PASSWORD=hackerputo24
```

#### Paso 4: Cambiar la contraseña
Reemplaza `hackerputo24` por tu nueva contraseña:
```bash
DJANGO_DEV_PASSWORD=MiNuevaContraseñaSegura123!
```

#### Paso 5: Guardar el archivo
Guarda los cambios en el archivo `.env`

#### Paso 6: Reiniciar el servidor Django
```bash
# En la terminal donde está corriendo el servidor:
# 1. Detén el servidor (Ctrl+C)
# 2. Vuelve a iniciarlo:
python manage.py runserver
```

**✅ ¡Listo! La nueva contraseña ya está activa.**

---

## 🚪 Cómo Acceder al Panel de Desarrollador

### Paso a paso:

1. **Inicia sesión en el sistema**
   - URL: http://127.0.0.1:8000/accounts/login/
   - Usuario: `admin`
   - Contraseña: [tu contraseña de admin Django]

2. **Ve al dashboard de administrador**
   - Deberías ver el menú lateral con opciones de administración

3. **Haz clic en "Panel Desarrollador"**
   - Está en la sección "HERRAMIENTAS TÉCNICAS" del menú lateral

4. **Ingresa la contraseña del panel desarrollador**
   - Contraseña actual: `hackerputo24`
   - Esta es la contraseña configurada en el archivo `.env`

5. **¡Acceso concedido!**
   - Serás redirigido al panel de administración técnica de Django
   - URL: http://127.0.0.1:8000/admin/

---

## 🔍 Entendiendo el Sistema de Doble Autenticación

### ¿Por qué dos contraseñas?

El sistema usa un enfoque de **seguridad en capas**:

#### Primera Capa: Usuario Django
- Usuario: `admin`
- Contraseña: La que estableciste con `python manage.py changepassword admin`
- Propósito: Autenticación básica del usuario
- Cambio: `python manage.py changepassword admin`

#### Segunda Capa: Panel Desarrollador
- Contraseña: `hackerputo24` (configurable en `.env`)
- Propósito: Protección adicional para acceso técnico
- Cambio: Editar variable `DJANGO_DEV_PASSWORD` en archivo `.env`

### ¿Quién puede acceder?

Solo usuarios que cumplan TODAS estas condiciones:
1. ✅ Estar autenticado en el sistema (primera contraseña)
2. ✅ Ser superusuario O ser administrador del holding
3. ✅ Conocer la contraseña del panel desarrollador (segunda contraseña)

---

## 📂 Ubicación Técnica

### Archivo de configuración:
```
Ruta: FinalPoo2/.env
Variable: DJANGO_DEV_PASSWORD
Valor actual: hackerputo24
```

### Código que valida la contraseña:
```
Archivo: empresas/views_dev_auth.py
Función: get_dev_password()
```

### Template del formulario:
```
Archivo: templates/empresas/admin/dev_auth.html
```

---

## 🛡️ Recomendaciones de Seguridad

1. ✅ **Usa contraseñas fuertes**
   - Mínimo 12 caracteres
   - Combina letras, números y símbolos
   - Evita palabras comunes

2. ✅ **No compartas las contraseñas**
   - Mantén las credenciales privadas
   - No las envíes por email o chat sin cifrar

3. ✅ **Cambia las contraseñas regularmente**
   - Especialmente si sospechas que fueron comprometidas

4. ✅ **El archivo .env NO se sube a GitHub**
   - Ya está en `.gitignore` por seguridad
   - Cada desarrollador tiene su propio `.env` local

5. ✅ **En producción usa contraseñas diferentes**
   - No uses las mismas contraseñas de desarrollo en producción

---

## ❓ Preguntas Frecuentes

### ¿Qué pasa si olvido la contraseña del panel desarrollador?
Simplemente ábrela el archivo `.env` y revisa o cambia el valor de `DJANGO_DEV_PASSWORD`.

### ¿Por qué no me deja acceder aunque la contraseña sea correcta?
Posibles razones:
1. No reiniciaste el servidor Django después de cambiar el `.env`
2. Tu usuario no es superusuario ni administrador del holding
3. Hay espacios extra en la contraseña del archivo `.env`

### ¿Puedo eliminar esta segunda capa de seguridad?
Técnicamente sí, pero NO es recomendado. Esta capa protege el acceso técnico al sistema.

### ¿La contraseña está cifrada en el archivo .env?
No, está en texto plano. Por eso el archivo `.env` NO se sube al repositorio y está en `.gitignore`.

---

## 🔧 Solución de Problemas

### Error: "Contraseña de desarrollador incorrecta"
**Causa:** La contraseña ingresada no coincide con `DJANGO_DEV_PASSWORD` del archivo `.env`

**Solución:**
1. Verifica que el archivo `.env` existe en la raíz del proyecto
2. Abre `.env` y revisa el valor de `DJANGO_DEV_PASSWORD`
3. Copia la contraseña exacta (sin espacios extra)
4. Si la cambiaste, reinicia el servidor Django

### Error: "No tienes permisos para acceder al panel de desarrollador"
**Causa:** Tu usuario no es administrador del holding

**Solución:**
1. Verifica que tu usuario sea superusuario: `user.is_superuser = True`
2. O asigna el rol de admin en el perfil empresa del usuario

### El servidor no reconoce la nueva contraseña
**Causa:** El servidor no recargó las variables de entorno

**Solución:**
1. Detén completamente el servidor Django (Ctrl+C)
2. Vuelve a iniciarlo: `python manage.py runserver`
3. Las variables de entorno se cargan al inicio del servidor

---

## 📅 Historial de Cambios

| Fecha | Cambio Realizado | Nueva Contraseña |
|-------|------------------|------------------|
| 06/11/2025 | Contraseña inicial establecida | `hackerputo24` |

---

## 📞 Contacto

Para soporte adicional, consulta:
- [Guía Completa de Cambio de Contraseñas](./cambio_password_admin.md)
- [Guía Rápida](./QUICK_START_PASSWORD.md)
- [README Principal](../README.md)

---

**Última actualización:** 6 de Noviembre de 2025  
**Versión:** 1.0
