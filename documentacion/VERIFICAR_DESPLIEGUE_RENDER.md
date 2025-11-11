# 🚀 Guía para Verificar y Solucionar Problemas de Despliegue en Render

## ❌ Error 503 - Servicio No Disponible

### Causas Comunes:

1. **Servicio en Estado "Sleeping" (Plan Gratuito)**
   - Render Free Tier suspende servicios inactivos después de 15 minutos
   - El primer request puede tardar 30-60 segundos en despertar el servicio
   - **Solución**: Espera 1 minuto y recarga la página

2. **Error en el Build o Deploy**
   - Falta de variables de entorno
   - Error en migraciones de base de datos
   - Dependencias faltantes o incompatibles

3. **Crash del Proceso de Gunicorn**
   - Error en settings.py
   - Base de datos no accesible
   - Memoria insuficiente (512MB en plan gratuito)

---

## 🔍 Cómo Verificar el Estado del Despliegue

### 1. Revisar Logs en Render Dashboard

```
1. Ir a: https://dashboard.render.com/
2. Seleccionar el servicio "finalpoo2"
3. Ver la pestaña "Logs"
4. Buscar errores en:
   - Build logs (instalación de dependencias)
   - Deploy logs (migraciones, collectstatic)
   - Runtime logs (errores de Gunicorn/Django)
```

### 2. Verificar Variables de Entorno Requeridas

Las siguientes variables DEBEN estar configuradas en Render:

```bash
✅ DATABASE_URL         # URL de PostgreSQL (proporcionada por Neon)
✅ SECRET_KEY           # Generada automáticamente por Render
✅ DEBUG                # Debe ser "False" en producción
✅ SENDGRID_API_KEY     # Clave API de SendGrid (para emails)
✅ EMAIL_HOST_USER      # Email del remitente
✅ DEFAULT_FROM_EMAIL   # Email por defecto (opcional)
✅ RENDER_EXTERNAL_HOSTNAME  # Autoconfigurada por Render
```

### 3. Verificar Estado del Servicio

En el dashboard de Render, busca:
- 🟢 **Live**: Servicio activo
- 🟡 **Building**: Compilando
- 🔴 **Failed**: Error en el despliegue
- ⚪ **Suspended**: Servicio suspendido (plan gratuito inactivo)

---

## 🛠️ Soluciones Paso a Paso

### Solución 1: Forzar Redeploy

Si el servicio está en estado suspendido o con error:

```bash
# En tu terminal local:
git commit --allow-empty -m "trigger: Forzar redeploy en Render"
git push origin master
```

Render automáticamente detectará el push y hará un nuevo deploy.

### Solución 2: Verificar Logs de Error

Mensajes comunes en los logs y sus soluciones:

#### Error: `SECRET_KEY no esta configurada`
```bash
Solución:
1. Ir a Render Dashboard → finalpoo2 → Environment
2. Verificar que SECRET_KEY existe
3. Si no existe, agregarla manualmente o usar "Generate Value"
```

#### Error: `DATABASE_URL no está configurada`
```bash
Solución:
1. Verificar que DATABASE_URL apunta a tu base de datos Neon
2. Formato: postgresql://user:password@host/database?sslmode=require
3. Verificar que la base de datos Neon está activa
```

#### Error: `django.db.utils.OperationalError: could not connect to server`
```bash
Solución:
1. Verificar que la base de datos Neon está activa (no suspendida)
2. Verificar las credenciales en DATABASE_URL
3. Verificar que la IP de Render está permitida en Neon
```

#### Error: `No module named 'XXX'`
```bash
Solución:
1. Verificar que el paquete está en requirements.txt
2. Forzar rebuild:
   - Render Dashboard → Settings → Manual Deploy → "Clear build cache & deploy"
```

### Solución 3: Reiniciar Servicio Manualmente

Desde el Dashboard de Render:
```
1. Ir a finalpoo2 → Settings
2. Scroll hasta "Suspend Service" o "Restart Service"
3. Click en "Restart Service"
4. Esperar 2-3 minutos para que el servicio inicie
```

### Solución 4: Verificar Healthcheck

Render hace healthcheck cada 30 segundos en la ruta raíz `/`.

Si tu app no responde en 30 segundos, Render la marca como "unhealthy".

**Optimización para plan gratuito:**
- Reducir workers de Gunicorn (ya configurado: 2 workers)
- Aumentar timeout (ya configurado: 120 segundos)
- Optimizar queries de base de datos

---

## 📊 Monitoreo en Tiempo Real

### Ver Logs en Vivo

```bash
# Desde el dashboard de Render:
1. Seleccionar "finalpoo2"
2. Click en "Logs"
3. Los logs se actualizan automáticamente
```

### Logs Importantes a Buscar:

```
✅ "Booting worker with pid"         → Gunicorn iniciando correctamente
✅ "Operations to perform: 0"        → Migraciones aplicadas
✅ "172 static files copied"         → Static files recopilados
❌ "ModuleNotFoundError"             → Falta dependencia
❌ "django.db.utils"                 → Error de base de datos
❌ "Worker timeout"                  → Proceso muy lento (optimizar)
```

---

## 🔄 Proceso de Deploy Normal

1. **Push a GitHub** → Código subido a `origin/master`
2. **Render detecta cambios** → Inicia build automático
3. **Build Phase** (3-5 minutos):
   - Instala dependencias (`pip install -r requirements.txt`)
   - Ejecuta `bash build.sh`
   - Collectstatic
   - Migraciones
4. **Deploy Phase** (1-2 minutos):
   - Inicia Gunicorn
   - Healthcheck
   - Servicio en vivo

**Total: 5-7 minutos** desde push hasta servicio activo.

---

## 🆘 Si Nada Funciona

### Verificación Completa:

1. ✅ ¿DATABASE_URL está configurada y es válida?
2. ✅ ¿SECRET_KEY está configurada?
3. ✅ ¿DEBUG=False en producción?
4. ✅ ¿Base de datos Neon está activa?
5. ✅ ¿Los logs muestran errores específicos?
6. ✅ ¿El servicio tiene suficiente memoria? (ver Metrics)

### Último Recurso: Deploy Manual

```bash
# 1. Clonar repo en nueva carpeta
git clone https://github.com/JUANESTEBANORTIZRENDON/FinalPoo2.git test-deploy
cd test-deploy

# 2. Crear .env con variables de producción
echo "DATABASE_URL=postgresql://..." > .env
echo "SECRET_KEY=..." >> .env
echo "DEBUG=False" >> .env

# 3. Probar localmente
pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput

# 4. Si funciona localmente, el problema está en Render
# Contactar soporte de Render con los logs
```

---

## 📞 Contacto de Soporte

- **Render Support**: https://render.com/docs/support
- **Render Community**: https://community.render.com/
- **GitHub Issues**: Crear issue en el repositorio

---

## 🎯 Checklist de Verificación Rápida

Antes de reportar un problema:

- [ ] Revisé los logs en Render Dashboard
- [ ] Verifiqué que todas las variables de entorno están configuradas
- [ ] Esperé 2 minutos después del deploy
- [ ] Intenté hacer un redeploy manual
- [ ] Verifiqué que la base de datos Neon está activa
- [ ] Probé en modo incógnito (sin cache del navegador)
- [ ] Revisé el estado del servicio en Render (Live/Failed/Suspended)

---

**Última actualización**: 11 de noviembre de 2025
**Versión**: 1.0
**Autor**: Equipo S_CONTABLE
