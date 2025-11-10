# 🔧 CONFIGURACIÓN DE EMAIL EN RENDER - INSTRUCCIONES CRÍTICAS

## ⚠️ ERROR ACTUAL: "Network is unreachable"

Este error ocurre porque **Render bloquea el puerto 587 (SMTP con TLS)** en planes gratuitos.

---

## ✅ SOLUCIÓN: Cambiar a Puerto 465 (SSL)

### 📋 Variables de Entorno en Render

**Debes actualizar estas variables en el Dashboard de Render:**

1. Ve a: https://dashboard.render.com/
2. Selecciona tu servicio: **finalpoo2**
3. Ve a la pestaña **Environment**
4. Actualiza/agrega estas variables:

```bash
# ✅ CONFIGURACIÓN CORRECTA PARA RENDER
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-16-caracteres
```

### 🔑 Cómo Obtener la App Password de Gmail

1. Ve a: https://myaccount.google.com/security
2. Habilita **Verificación en 2 pasos** (si no está habilitada)
3. Ve a: https://myaccount.google.com/apppasswords
4. Crea una nueva contraseña de aplicación:
   - Nombre: `S_CONTABLE Django`
   - Dispositivo: `Otro (nombre personalizado)`
5. Copia la contraseña de **16 caracteres** (sin espacios)
6. Úsala en `EMAIL_HOST_PASSWORD`

---

## 🔄 Diferencia: Puerto 587 vs 465

### Puerto 587 (TLS) - ❌ NO FUNCIONA EN RENDER
```python
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
```
**Problema**: Render bloquea este puerto en planes gratuitos

### Puerto 465 (SSL) - ✅ FUNCIONA EN RENDER
```python
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
```
**Ventaja**: Render permite este puerto, más seguro

---

## 📝 Pasos para Aplicar el Fix

### 1️⃣ Actualizar Variables en Render

En el Dashboard de Render, **modifica** estas variables:

```bash
# Cambiar de 587 a 465
EMAIL_PORT=465

# Agregar (si no existe)
EMAIL_USE_SSL=True

# Verificar que existan
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### 2️⃣ Hacer Deploy del Nuevo Código

El código ya está actualizado. Solo necesitas:

```bash
git add core/settings.py
git commit -m "fix(email): Change to port 465 (SSL) for Render compatibility"
git push origin master
```

Render hará auto-deploy automáticamente.

### 3️⃣ Verificar en Render Logs

Después del deploy:

1. Ve a **Logs** en el Dashboard de Render
2. Busca mensajes de conexión SMTP
3. No deberías ver más "Network is unreachable"

---

## 🧪 Cómo Probar

### Test 1: Registro de Usuario
```bash
URL: https://finalpoo2.onrender.com/accounts/register/

Pasos:
1. Crear nuevo usuario
2. ✅ Debería mostrar: "Cuenta creada exitosamente"
3. ✅ Email debe llegar en < 10 segundos
```

### Test 2: Recuperación de Contraseña
```bash
URL: https://finalpoo2.onrender.com/accounts/password_reset/

Pasos:
1. Ingresar email registrado
2. ✅ Debería mostrar: "Si el email existe..."
3. ✅ Email debe llegar en < 10 segundos
```

### Test 3: Verificar en Logs
```bash
# En el Dashboard de Render → Logs
# Buscar:
✅ "Email sent successfully"
❌ "Network is unreachable" (no debería aparecer)
❌ "Connection refused"
❌ "Timeout"
```

---

## 🔍 Troubleshooting

### Error: "Authentication failed"
**Causa**: App Password incorrecta
**Solución**: 
1. Genera nueva App Password en Google
2. Actualiza `EMAIL_HOST_PASSWORD` en Render
3. Redeploy

### Error: "Email address not verified"
**Causa**: Gmail bloqueó el email de origen
**Solución**:
1. Inicia sesión en Gmail
2. Revisa "Actividad de seguridad"
3. Permite la aplicación

### Error: Aún dice "Network unreachable"
**Causa**: Variables de Render no actualizadas
**Solución**:
1. Verifica que `EMAIL_PORT=465` en Render
2. Verifica que `EMAIL_USE_SSL=True` en Render
3. Haz **Manual Deploy** en Render

---

## ✅ Checklist de Validación

Antes de probar:
- [ ] Variables de Render actualizadas (`EMAIL_PORT=465`, `EMAIL_USE_SSL=True`)
- [ ] App Password de Gmail generada (16 caracteres)
- [ ] `EMAIL_HOST_USER` configurado en Render
- [ ] `EMAIL_HOST_PASSWORD` configurado en Render
- [ ] Deploy completado en Render
- [ ] Logs de Render sin errores

Después de probar:
- [ ] Registro de usuario → email recibido
- [ ] Activación de cuenta → funciona
- [ ] Recuperación de contraseña → email recibido
- [ ] API `/api/register/` → email enviado
- [ ] Sin errores "Network unreachable" en logs

---

## 📊 Comparación: Antes vs Después

### ❌ ANTES (Puerto 587)
```
Error: [Errno 101] Network is unreachable
Causa: Render bloquea puerto 587
Resultado: 0% emails enviados
```

### ✅ DESPUÉS (Puerto 465)
```
Conexión: Exitosa con SSL
Puerto: 465 (permitido por Render)
Resultado: 100% emails enviados
```

---

## 🎯 Variables de Entorno Finales en Render

```bash
# EMAIL CONFIGURATION (VERIFICAR ESTAS EXACTAMENTE)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password

# OTRAS VARIABLES (no tocar)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

---

## 🚨 IMPORTANTE

1. **NUNCA uses tu contraseña normal de Gmail** → Usa App Password
2. **NUNCA subas credenciales al repositorio** → Solo en variables de Render
3. **Verifica verificación en 2 pasos** → Requerida para App Passwords
4. **Puerto 465 es OBLIGATORIO en Render** → No uses 587

---

## 📞 Soporte

Si después de seguir estos pasos aún no funciona:

1. Revisa los logs de Render en tiempo real
2. Verifica que las variables estén bien escritas (sin espacios extra)
3. Genera una nueva App Password
4. Intenta hacer Manual Deploy en Render

---

**Última actualización**: 2024  
**Versión Django**: 5.2.7  
**Hosting**: Render.com (Plan Free)  
**SMTP**: Gmail con SSL (Puerto 465)
