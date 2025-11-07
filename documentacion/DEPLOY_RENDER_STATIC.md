# 🚀 Guía de Despliegue en Render - S_CONTABLE

## 📋 Requisitos Previos

- Cuenta en [Render](https://render.com)
- Repositorio en GitHub con el código
- Base de datos PostgreSQL (Neon o Render PostgreSQL)

## 🔧 Configuración en Render

### 1️⃣ Crear Web Service

1. Ve a [Render Dashboard](https://dashboard.render.com)
2. Click en **"New +"** → **"Web Service"**
3. Conecta tu repositorio de GitHub
4. Configura:
   - **Name**: `finalpoo2` (o tu nombre preferido)
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn core.wsgi:application`

### 2️⃣ Variables de Entorno Requeridas

Agrega las siguientes variables en **Environment** → **Add Environment Variable**:

#### 🔐 Seguridad
```bash
SECRET_KEY=<tu_clave_secreta_django>
DEBUG=False
ALLOWED_HOSTS=finalpoo2.onrender.com,*.onrender.com
```

**Generar SECRET_KEY**:
```bash
python generate_secret_key.py
```

#### 🗄️ Base de Datos
```bash
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**Obtener de Neon**:
- Dashboard → Connection String → Pooled connection

#### 📧 Email (Gmail SMTP)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
```

**Obtener Gmail App Password**:
1. Google Account → Security → 2-Step Verification
2. App passwords → Generate

#### 🔒 Panel de Desarrollador
```bash
DJANGO_DEV_PASSWORD=tu_contraseña_segura
```

**Recomendación**: Usa una contraseña fuerte diferente a la de desarrollo.

### 3️⃣ Verificar Configuración de Estáticos

Render automáticamente:
1. Ejecuta `./build.sh`
2. Recolecta archivos estáticos con `collectstatic`
3. Verifica assets con `check_admin_assets`
4. Ejecuta migraciones

**NO configures** `DISABLE_COLLECTSTATIC=1` (debe estar habilitado).

## 🎨 Verificación de Estilos del Admin

### Después del Deploy

1. **Accede al admin**:
   ```
   https://tuapp.onrender.com/empresas/dev-auth/
   ```
   - Contraseña: La de `DJANGO_DEV_PASSWORD`

2. **Verifica que se vean**:
   - ✅ Sidebar colapsable con gradiente
   - ✅ Cards con estadísticas (usuarios, empresas, perfiles)
   - ✅ Tema neón (verde/azul)
   - ✅ Iconos y animaciones

### Si NO se ven los estilos

#### Paso 1: Verificar en Logs de Render

```bash
# En Render Dashboard → Logs, busca:
"Recolectando archivos estáticos..."
"166 static files copied to '/opt/render/project/src/staticfiles'"
```

#### Paso 2: Verificar assets desde SSH

```bash
# En Render Shell (Dashboard → Shell)
python manage.py check_admin_assets --verbose
```

Deberías ver:
```
✅ admin/css/admin_custom.css
✅ admin/js/sidebar.js
✅ WhiteNoiseMiddleware en posición correcta
✅ Template usa {% load static %}
```

#### Paso 3: Verificar en navegador

1. Abre DevTools (F12) → Network
2. Recarga `/admin/`
3. Busca:
   ```
   /static/admin/css/admin_custom.css → 200 OK
   /static/admin/js/sidebar.js → 200 OK
   ```

#### Paso 4: Verificar archivos directamente

Accede a:
```
https://tuapp.onrender.com/static/admin/css/admin_custom.css
https://tuapp.onrender.com/static/admin/js/sidebar.js
```

Deben devolver **200 OK** y mostrar el contenido.

## 🔧 Solución de Problemas Comunes

### Error: "404 Not Found" en archivos estáticos

**Causa**: `collectstatic` no se ejecutó o falló.

**Solución**:
1. Verifica logs de build en Render
2. Asegúrate que `build.sh` tiene permisos de ejecución:
   ```bash
   chmod +x build.sh
   ```
3. Forzar redeploy: Dashboard → Manual Deploy → Deploy latest commit

### Error: Estilos se ven pero sin tema personalizado

**Causa**: Cache del navegador.

**Solución**:
1. Ctrl + Shift + R (hard reload)
2. O borra cache del navegador
3. Verifica que los archivos CSS tienen el contenido correcto (accede directo a la URL)

### Error: "Mixed Content" en HTTPS

**Causa**: Referencias a recursos HTTP en página HTTPS.

**Solución**:
1. Verifica en DevTools → Console
2. Cambia todos los CDN a HTTPS:
   ```html
   <!-- ❌ MAL -->
   <link href="http://cdn.example.com/style.css">
   
   <!-- ✅ BIEN -->
   <link href="https://cdn.example.com/style.css">
   ```

### Error: WhiteNoise no sirve archivos

**Causa**: Middleware en orden incorrecto.

**Solución**:
Verifica en `settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ← DEBE ir aquí
    # ... resto de middleware
]
```

## 📊 Comando de Diagnóstico

```bash
# Ejecuta en local antes de deploy
python manage.py check_admin_assets --verbose

# Ejecuta en Render Shell después de deploy
python manage.py check_admin_assets
```

Salida esperada:
```
🔍 Verificando configuración de assets del admin...

✅ admin/css/admin_custom.css
✅ admin/js/sidebar.js
✅ STATIC_URL = /static/
✅ STATIC_ROOT configurado
✅ WhiteNoiseMiddleware en posición correcta
✅ Template usa {% load static %}

✨ ¡TODO ESTÁ CORRECTO!
```

## 🔄 Workflow de Actualización

### Después de cambios en templates/CSS/JS:

```bash
# 1. Commit y push
git add .
git commit -m "feat: actualizar estilos del admin"
git push origin master

# 2. Render auto-detecta y redeploys
# O forzar: Dashboard → Manual Deploy

# 3. Esperar a que termine el build (2-3 min)

# 4. Verificar en navegador (Ctrl+Shift+R)
```

## 📝 Checklist Pre-Deploy

- [ ] Todas las variables de entorno configuradas en Render
- [ ] `SECRET_KEY` diferente a la de desarrollo
- [ ] `DEBUG=False` en producción
- [ ] `DJANGO_DEV_PASSWORD` configurada (no usar la de desarrollo)
- [ ] `DATABASE_URL` apunta a Neon (no a base local)
- [ ] `build.sh` tiene permisos de ejecución
- [ ] `python manage.py check_admin_assets` pasa en local
- [ ] `whitenoise` en `requirements.txt`
- [ ] Archivos en `static/admin/css/` y `static/admin/js/` commiteados

## 🎯 URLs Importantes en Producción

```
Login:           https://tuapp.onrender.com/accounts/login/
Dev Auth:        https://tuapp.onrender.com/empresas/dev-auth/
Django Admin:    https://tuapp.onrender.com/admin/
Dashboard:       https://tuapp.onrender.com/empresas/admin/dashboard/
```

## 🔐 Credenciales por Defecto

⚠️ **CAMBIAR EN PRODUCCIÓN**

- **Usuario Admin Django**: `admin` / `Admin123!`
- **Panel Desarrollador**: Ver `DJANGO_DEV_PASSWORD` en Render

## 📚 Referencias

- [Render Django Docs](https://render.com/docs/deploy-django)
- [WhiteNoise Docs](http://whitenoise.evans.io/)
- [Django Static Files](https://docs.djangoproject.com/en/5.2/howto/static-files/)
- [Neon PostgreSQL](https://neon.tech/docs)

---

**Fecha actualización**: 6 de noviembre de 2025  
**Versión Django**: 5.2.7  
**Versión Python**: 3.11
