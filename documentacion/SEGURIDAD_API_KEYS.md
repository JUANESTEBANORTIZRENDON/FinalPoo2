# 🔒 GUÍA DE SEGURIDAD: Gestión de API Keys

## ⚠️ IMPORTANTE: NUNCA Subir API Keys al Repositorio

### 🚨 ¿Qué Pasó?

GitHub detectó que una API key de SendGrid fue subida al repositorio público y la **eliminó automáticamente** por seguridad.

**Email recibido de GitHub**:
```
Tu clave API de Twilio SendGrid ha sido eliminada

Hemos detectado que una clave API perteneciente al titular de una cuenta 
de Twilio SendGrid está publicada en línea. Para evitar el acceso y la 
modificación no autorizados de su cuenta, esta clave ha sido eliminada.
```

---

## ✅ SOLUCIÓN APLICADA

### 1️⃣ Nueva API Key Generada
- Vieja API Key: `SG.thshMMGeSCOn2h08uG-SXQ...` ❌ (eliminada por GitHub)
- Nueva API Key: `SG.Vm_y6Ea7SDair7kZye5b6g...` ✅ (privada)

### 2️⃣ Limpieza del Repositorio
- ✅ Removida API key del código fuente
- ✅ Actualizado `.gitignore` para excluir `.env`
- ✅ Scripts actualizados para usar variables de entorno
- ✅ Sin API keys hardcodeadas en el código

### 3️⃣ Configuración Segura
- ✅ API keys solo en variables de entorno
- ✅ `.env` local (NO se sube a GitHub)
- ✅ Variables de entorno en Render (seguras)

---

## 📋 DÓNDE van las API Keys

### ❌ NUNCA aquí:
- Código fuente (`.py`, `.js`, etc.)
- Archivos de configuración versionados
- Commits de Git
- Documentación en el repo
- Comentarios en el código

### ✅ SIEMPRE aquí:
- Archivo `.env` local (en `.gitignore`)
- Variables de entorno en Render
- Gestores de secretos (Vault, AWS Secrets, etc.)

---

## 🛡️ BUENAS PRÁCTICAS

### 1. Archivo `.env` Local
```bash
# .env (NUNCA subir a Git)
SENDGRID_API_KEY=SG.xxxxx...
EMAIL_HOST_USER=tu-email@gmail.com
```

### 2. `.gitignore`
```bash
# Archivo .gitignore
.env
*.env
.env.local
.env.production
```

### 3. Código Seguro
```python
# ✅ CORRECTO
import os
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# ❌ INCORRECTO
SENDGRID_API_KEY = "SG.xxxxx..."  # NUNCA así
```

### 4. Variables en Render
```
Dashboard → Environment → Add Environment Variable
```

---

## 🔄 SI Expones una API Key

### Pasos Inmediatos:

1. **Revocar la API key comprometida**
   - Ve a SendGrid: https://app.sendgrid.com/settings/api_keys
   - Elimina la API key expuesta

2. **Generar nueva API key**
   - Crea una nueva con Full Access
   - Guárdala de forma segura

3. **Actualizar variables de entorno**
   - Local: Actualiza `.env`
   - Render: Actualiza en Dashboard

4. **Limpiar historial de Git (si es necesario)**
   ```bash
   # Reescribir último commit
   git commit --amend --no-edit
   git push origin master --force
   ```

5. **Verificar que funcione**
   ```bash
   python test_sendgrid.py
   python test_django_email.py
   ```

---

## 🎯 CHECKLIST DE SEGURIDAD

Antes de cada commit:

- [ ] No hay API keys en el código
- [ ] `.env` está en `.gitignore`
- [ ] Variables de entorno usan `os.getenv()`
- [ ] Documentación no contiene secretos
- [ ] Commits no exponen credenciales

Antes de cada deploy:

- [ ] Variables configuradas en Render
- [ ] API keys son válidas y activas
- [ ] Emails de prueba funcionan
- [ ] Logs no muestran secretos

---

## 📧 CONFIGURACIÓN ACTUAL (SEGURA)

### Variables de Entorno en Render:

```bash
# ✅ CONFIGURACIÓN SEGURA
SENDGRID_API_KEY=<tu-api-key-aqui>  # Nueva API key
EMAIL_HOST_USER=juanestebanortizrendon24072004@gmail.com
DEFAULT_FROM_EMAIL=juanestebanortizrendon24072004@gmail.com
```

### Verificación:
```bash
# En SendGrid Dashboard
https://app.sendgrid.com/

Settings → API Keys → Verificar que existe la nueva key
Activity → Email Activity → Ver emails enviados
```

---

## 🚀 PRÓXIMOS PASOS

1. **Actualizar variables en Render**:
   - Dashboard → finalpoo2 → Environment
   - Cambiar `SENDGRID_API_KEY` a la nueva
   - Save Changes

2. **Esperar deploy**:
   - Render hará auto-deploy (~5 min)
   - Verificar en Logs que no haya errores

3. **Probar en producción**:
   - Registro de usuario
   - Recuperación de contraseña
   - Verificar email recibido

4. **Monitorear SendGrid**:
   - Dashboard → Email Activity
   - Verificar deliverability
   - Revisar bounces/errores

---

## 📚 RECURSOS

- [GitHub Secret Scanning](https://docs.github.com/code-security/secret-scanning)
- [SendGrid API Keys Best Practices](https://docs.sendgrid.com/ui/account-and-settings/api-keys)
- [Django Environment Variables](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)

---

**Última actualización**: 2024  
**Estado**: ✅ API Keys seguras y funcionales  
**Ambiente**: Producción (Render) + Desarrollo (Local)
